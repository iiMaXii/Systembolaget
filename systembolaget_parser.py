#!/usr/bin/env python3

import sqlite3
import xml.etree.ElementTree
import common
import unicodedata
import re
import urllib.request
from common import PROPERTY_TYPES
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


def calculate_alcohol_per_sek(volume: int, price: int,
                              alcohol_percentage: int):
    alcohol_ratio = alcohol_percentage / 100 / 100
    return int(100 * round((volume * alcohol_ratio) / price, 2))


def create_tables(conn: sqlite3.Connection):
    expr = []
    for p in PROPERTY_TYPES:
        expr.append('{} {}'.format(p.identifier, common.get_type_str(p.type)))

    expr.append('PRIMARY KEY ({})'.format(PROPERTY_TYPES[0].identifier))

    cursor = conn.cursor()
    main_table = ('CREATE TABLE sortiment ({})'.format(', \n'.join(expr)))

    cursor.execute(main_table)
    conn.commit()


def add_items(conn: sqlite3.Connection, items: SystembolagetSortiment):
    cur = conn.cursor()

    insertion_list = []
    for item in items.items:
        row = []
        for p in PROPERTY_TYPES:
            if p.identifier in item:
                row.append(item[p.identifier])
            else:
                row.append(None)

        insertion_list.append(row)

    cur.executemany('INSERT INTO sortiment({}) values ({})'
                    .format(', '.join([p.identifier for p in PROPERTY_TYPES]),
                            ', '.join('?' * len(PROPERTY_TYPES))),
                    insertion_list)

    conn.commit()


def parse_property(property_value: str, property_type: PropertyType):
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
    elif property_type == PropertyType.PERCENTAGE:
        if not property_value.endswith('%') or property_value[-4] != '.':
            raise Exception('Malformed percentage property')

        return int(property_value[:-4] + property_value[-3:-1])
    else:  # TEXT, DATE, CATEGORY
        return property_value


def get_items(assortment_xml: str) -> SystembolagetSortiment:
    e = xml.etree.ElementTree.fromstring(assortment_xml)

    created = e.find('skapad-tid').text
    message = e.find('info').find('meddelande').text

    property_categories = {}
    items = []

    for article in e.findall('artikel'):
        item_properties = {}

        for xml_prop in article:
            prop = None
            for p in PROPERTY_TYPES:
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
                                                           prop.type)

        a = calculate_alcohol_per_sek(item_properties['Volymiml'],
                                      item_properties['Prisinklmoms'],
                                      item_properties['Alkoholhalt'])
        item_properties['AlkoholPerKrona'] = a

        items.append(item_properties)

    return SystembolagetSortiment(created, message, property_categories, items)


if __name__ == "__main__":
    conn = sqlite3.connect('sortiment.db')

    create_tables(conn)

    data = urllib.request.urlopen(
        'https://www.systembolaget.se/api/assortment/products/xml').read()

    items = get_items(data)

    add_items(conn, items)

    conn.close()
