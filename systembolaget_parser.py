#!/usr/bin/env python3

import sqlite3
import xml.etree.ElementTree
import common
import unicodedata
import re
from common import PROPERTY_TYPES_2
from common import PropertyType
from common import VARUGRUPP_URL


class SystembolagetSortiment:
    def __init__(self, created, message, property_categories, items):
        self.created = created
        self.message = message
        self.property_categories = property_categories
        self.items = items

    def __len__(self):
        return len(self.items)

    def __iter__(self):
        return iter(self.items)


def get_url(nr, varugrupp, name: str):
    category_serialized = VARUGRUPP_URL[varugrupp]
    name = name.lower()
    name = name.replace(' ', '-')
    name = str(unicodedata.normalize('NFKD', name).encode('ascii', 'ignore'),
               'ascii')
    pattern = re.compile('[^A-Za-z0-9\-]+')
    name = pattern.sub('', name)
    name = name.replace('--', '-')

    return ('https://www.systembolaget.se/dryck/{}/{}-{}'
            .format(category_serialized, name, nr))

#import sys
#print(get_url('54502', 'Punsch', 'Tegnér & Son Punsch'))
#print(get_url('8629102', 'Tequila och Mezcal', 'Los Tres Toños'))
#sys.exit()


def calculate_alcohol_per_sek(volume: int, price: int,
                              alcohol_percentage: int):
    alcohol_ratio = alcohol_percentage / 100 / 100
    #volume = volume / 100
    #price = price / 100
    return int(100 * round((volume * alcohol_ratio) / price, 2))


def create_tables(conn: sqlite3.Connection):
    expr = []
    for p in PROPERTY_TYPES_2:
        if p.type == PropertyType.CATEGORY:
            e = '{} {} DEFAULT 0 NOT NULL'.format(p.identifier,
                                                  common.get_type_str(p.type))
        else:
            e = '{} {}'.format(p.identifier, common.get_type_str(p.type))

        expr.append(e)

    expr.append('PRIMARY KEY ({})'
                .format(PROPERTY_TYPES_2[0].identifier))

    category_tables = []
    for p in PROPERTY_TYPES_2:
        if p.type == PropertyType.CATEGORY:
            expr.append('FOREIGN KEY ({}) REFERENCES kategori_{}(ID)'
                        .format(p.identifier, p.identifier))

            category_tables.append('CREATE TABLE kategori_{} (ID INTEGER, '
                                   'Name TEXT, PRIMARY KEY (ID))'
                                   .format(p.identifier))

    cursor = conn.cursor()
    for cat in category_tables:
        cursor.execute(cat)

    main_table = ('CREATE TABLE sortiment ({})'
                  .format(', \n'.join(expr)))

    cursor.execute(main_table)

    conn.commit()


def add_categories(conn: sqlite3.Connection, items: SystembolagetSortiment):
    cur = conn.cursor()

    for category, values in items.property_categories.items():
        cur.executemany('INSERT INTO kategori_{}(ID, Name) values (?, ?)'
                        .format(category), enumerate(values))

    conn.commit()


def add_items(conn: sqlite3.Connection, items: SystembolagetSortiment):
    cur = conn.cursor()

    insertion_list = []
    for item in items.items:
        row = []
        for p in PROPERTY_TYPES_2:
            if p.identifier in item:
                row.append(item[p.identifier])
            elif p.type == PropertyType.CATEGORY:
                row.append(0)
            else:
                row.append(None)

        insertion_list.append(row)

    cur.executemany('INSERT INTO sortiment({}) values ({})'
                    .format(', '.join([p.identifier for p in PROPERTY_TYPES_2]),
                            ', '.join('?'*len(PROPERTY_TYPES_2))),
                    insertion_list)

    conn.commit()


def parse_property(property_value: str, property_type: PropertyType,
                   property_name: str, property_categories: dict):
    if property_type == PropertyType.INTEGER:
        if not property_value:
            return None
        return int(property_value)
    elif (property_type == PropertyType.PRICE or
          property_type == PropertyType.PRICE_PER_LITER or
          property_type == PropertyType.VOLUME):
        if property_value[-3] != '.':
            raise Exception('Malformed price or volume property')
        return int(property_value[:-3] + property_value[-2:])
    elif property_type == PropertyType.BOOLEAN:
        return bool(int(property_value))
    elif property_type == PropertyType.CATEGORY:
        if (property_name not in property_categories or
                property_value not in property_categories[property_name]):
            return 0
        return property_categories[property_name].index(property_value)
    elif property_type == PropertyType.PERCENTAGE:
        if not property_value.endswith('%') or property_value[-4] != '.':
            raise Exception('Malformed percentage property')

        return int(property_value[:-4] + property_value[-3:-1])
    else:  # TEXT, DATE
        return property_value


def get_items(assortment_file) -> SystembolagetSortiment:
    e = xml.etree.ElementTree.parse(assortment_file).getroot()

    created = e.find('skapad-tid').text
    message = e.find('info').find('meddelande').text

    property_categories = {}
    items = []

    for article in e.findall('artikel'):
        item_properties = {}

        for xml_prop in article:
            prop = None
            for p in PROPERTY_TYPES_2:
                if p.identifier == xml_prop.tag:
                    prop = p
                    break

            if not prop:
                raise Exception('Unknown property')  # TODO custom exception

            if prop.type == PropertyType.CATEGORY and xml_prop.text:
                names = property_categories.get(xml_prop.tag,
                                                ['Ospecificerad'])
                if xml_prop.text not in names:
                    names.append(xml_prop.text)
                    property_categories[xml_prop.tag] = names

            item_properties[xml_prop.tag] = parse_property(xml_prop.text,
                                                           prop.type,
                                                           xml_prop.tag,
                                                           property_categories)

        a = calculate_alcohol_per_sek(item_properties['Volymiml'],
                                      item_properties['Prisinklmoms'],
                                      item_properties['Alkoholhalt'])
        item_properties['AlkoholPerKrona'] = a

        items.append(item_properties)

    return SystembolagetSortiment(created, message, property_categories, items)


if __name__ == "__main__":
    conn = sqlite3.connect('sortiment.db')

    create_tables(conn)

    items = get_items('Sortimentsfilen.xml')

    add_categories(conn, items)
    add_items(conn, items)

    conn.close()
