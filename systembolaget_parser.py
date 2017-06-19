#!/usr/bin/env python3

from enum import Enum
from collections import OrderedDict
import sqlite3
import xml.etree.ElementTree
import unicodedata


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


class PropertyType(Enum):
    INTEGER = 0
    TEXT = 1
    BOOLEAN = 2
    CATEGORY = 3
    DATE = 4
    PERCENTAGE = 5
    PRICE = 6
    PRICE_PER_LITER = 7
    ALCOHOL_PER_SEK = 8
    VOLUME = 9
    URL = 10


class SystembolagetProperty:
    def __init__(self, identifier: str, type: PropertyType, name: str,
                 visible: bool):
        self.identifier = identifier
        self.type = type
        self.name = name
        self.visible = visible

PROPERTY_TYPES_2 = [
    SystembolagetProperty('nr', PropertyType.INTEGER, 'Nummer', False),
    SystembolagetProperty('Artikelid', PropertyType.INTEGER, 'Artikelnummer', False),
    SystembolagetProperty('Varnummer', PropertyType.INTEGER, 'Varnummer', False),
    SystembolagetProperty('Namn', PropertyType.TEXT, 'Namn', True),
    SystembolagetProperty('Namn2', PropertyType.TEXT, 'Namn2', True),
    SystembolagetProperty('Prisinklmoms', PropertyType.PRICE, 'Pris inkl. moms', True),
    SystembolagetProperty('Pant', PropertyType.PRICE, 'Pant', False),
    SystembolagetProperty('Volymiml', PropertyType.VOLUME, 'Volym', True),
    SystembolagetProperty('PrisPerLiter', PropertyType.PRICE_PER_LITER, 'Pris per liter', True),
    SystembolagetProperty('Saljstart', PropertyType.DATE, 'Säljstart', False),
    SystembolagetProperty('Utgått', PropertyType.BOOLEAN, 'Utgått', False),
    SystembolagetProperty('Varugrupp', PropertyType.CATEGORY, 'Varugrupp', True),
    SystembolagetProperty('Typ', PropertyType.CATEGORY, 'Typ', True),
    SystembolagetProperty('Stil', PropertyType.CATEGORY, 'Stil', True),
    SystembolagetProperty('Forpackning', PropertyType.CATEGORY, 'Förpackning', False),
    SystembolagetProperty('Forslutning', PropertyType.CATEGORY, 'Förslutning', False),
    SystembolagetProperty('Ursprung', PropertyType.CATEGORY, 'Ursprung', True),
    SystembolagetProperty('Ursprunglandnamn', PropertyType.CATEGORY, 'Ursprungsland', True),
    SystembolagetProperty('Producent', PropertyType.CATEGORY, 'Producent', True),
    SystembolagetProperty('Leverantor', PropertyType.CATEGORY, 'Leverantör', False),
    SystembolagetProperty('Argang', PropertyType.INTEGER, 'Årgång', False),
    SystembolagetProperty('Provadargang', PropertyType.TEXT, 'Provad årgang', False),
    SystembolagetProperty('Alkoholhalt', PropertyType.PERCENTAGE, 'Alkoholhalt', True),
    SystembolagetProperty('Sortiment', PropertyType.CATEGORY, 'Sortiment', False),
    SystembolagetProperty('SortimentText', PropertyType.CATEGORY, 'Sortiment text', False),
    SystembolagetProperty('Ekologisk', PropertyType.BOOLEAN, 'Ekologisk', False),
    SystembolagetProperty('Etiskt', PropertyType.BOOLEAN, 'Etiskt', False),
    SystembolagetProperty('EtisktEtikett', PropertyType.CATEGORY, 'Etiskt etikett', False),
    SystembolagetProperty('Koscher', PropertyType.BOOLEAN, 'Koscher', False),
    SystembolagetProperty('RavarorBeskrivning', PropertyType.TEXT, 'Råvaror beskrivning', False),
    SystembolagetProperty('AlkoholPerKrona', PropertyType.ALCOHOL_PER_SEK, 'Alkohol per krona', False)]


def get_property_by_identifier(identifier: str) -> SystembolagetProperty:
    for p in PROPERTY_TYPES_2:
        if identifier == p.identifier:
            return p

    return None


PROPERTY_TYPES = OrderedDict([
    ('nr', PropertyType.INTEGER),  # Primary key
    ('Artikelid', PropertyType.INTEGER),
    ('Varnummer', PropertyType.INTEGER),
    ('Namn', PropertyType.TEXT),
    ('Namn2', PropertyType.TEXT),
    ('Prisinklmoms', PropertyType.PRICE),
    ('Pant', PropertyType.PRICE),
    ('Volymiml', PropertyType.VOLUME),
    ('PrisPerLiter', PropertyType.PRICE_PER_LITER),
    ('Saljstart', PropertyType.DATE),
    ('Utgått', PropertyType.BOOLEAN),
    ('Varugrupp', PropertyType.CATEGORY),
    ('Typ', PropertyType.CATEGORY),
    ('Stil', PropertyType.CATEGORY),
    ('Forpackning', PropertyType.CATEGORY),
    ('Forslutning', PropertyType.CATEGORY),
    ('Ursprung', PropertyType.CATEGORY),
    ('Ursprunglandnamn', PropertyType.CATEGORY),
    ('Producent', PropertyType.CATEGORY),
    ('Leverantor', PropertyType.CATEGORY),
    ('Argang', PropertyType.INTEGER),
    ('Provadargang', PropertyType.TEXT),
    ('Alkoholhalt', PropertyType.PERCENTAGE),
    ('Sortiment', PropertyType.CATEGORY),
    ('SortimentText', PropertyType.CATEGORY),
    ('Ekologisk', PropertyType.BOOLEAN),
    ('Etiskt', PropertyType.BOOLEAN),
    ('EtisktEtikett', PropertyType.CATEGORY),
    ('Koscher', PropertyType.BOOLEAN),
    ('RavarorBeskrivning', PropertyType.TEXT),
    ('AlkoholPerKrona', PropertyType.ALCOHOL_PER_SEK)])  # Beräknat


VARUGRUPP_URL = {
    'Okryddad sprit': 'sprit',
    'Vitt vin': 'vita-viner',
    'R\u00f6tt vin': 'roda-viner',
    'Mousserande vin': 'mousserande-viner',
    '\u00d6l': 'ol',
    'Tequila och Mezcal': 'sprit',
    'Whisky': 'sprit',
    'Ros\u00e9vin': 'roseviner',
    'Cognac': 'sprit',
    'Kryddad sprit': 'sprit',
    'Portvin': 'aperitif-dessert',
    'Montilla': 'aperitif-dessert',
    'Rom': 'sprit',
    'Lik\u00f6r': 'sprit',
    'Gin': 'sprit',
    'Brandy och Vinsprit': 'sprit',
    'Gl\u00f6gg och Gl\u00fchwein': 'aperitif-dessert',
    'Cider': 'cider-och-blanddrycker',
    'Vin av flera typer': 'aperitif-dessert',
    'Smaksatt sprit': 'sprit',
    'Fruktvin': 'aperitif-dessert',
    '\u00d6vrig sprit': 'sprit',
    'Alkoholfritt': 'alkoholfritt',
    'Sprit av frukt': 'sprit',
    'Bitter': 'sprit',
    'Sherry': 'aperitif-dessert',
    'Grappa och Marc': 'sprit',
    '\u00d6vrigt starkvin': 'aperitif-dessert',
    'Mj\u00f6d': 'aperitif-dessert',
    'Aperitif': 'aperitif-dessert',
    'Smaksatt vin': 'aperitif-dessert',
    'Sake': 'aperitif-dessert',
    'Calvados': 'sprit',
    'Genever': 'sprit',
    'Blanddrycker': 'cider-och-blanddrycker',
    'Vermouth': 'aperitif-dessert',
    'Drinkar och Cocktails': 'sprit',
    'Armagnac': 'sprit',
    'Aniskryddad sprit': 'sprit',
    'Punsch': 'sprit',
    'Madeira': 'aperitif-dessert',
    'Vita': 'vita-viner',
    'Snaps': 'sprit',
    'R\u00f6da': 'roda-viner',
    'Ros\u00e9': 'roseviner'
}


def first(i):
    """Return the first element from an ordered collection"""
    return next(iter(i))


import re, string


def get_url(nr, varugrupp, name: str):
    category_serialized = VARUGRUPP_URL[varugrupp]
    name = name.lower()
    name = name.replace(' ', '-')
    name = str(unicodedata.normalize('NFKD', name).encode('ascii', 'ignore'), 'ascii')
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


def format_real(value: int):
    if value < 100:
        return '0,{:02}'.format(value)

    s = str(value)

    return '{},{}'.format(s[:-2], s[-2:])


def format_value(value, property_type: PropertyType):
    if property_type == PropertyType.BOOLEAN:
        return 'Ja' if value else 'Nej'
    elif property_type == PropertyType.PERCENTAGE:
        return '{} %'.format(format_real(value))  # TODO
    elif property_type == PropertyType.PRICE:
        if not value:
            return ''

        #s = str(value)
        return '{} kr'.format(format_real(value))
    elif property_type == PropertyType.PRICE_PER_LITER:
        return '{} kr/l'.format(format_real(value))
    elif property_type == PropertyType.ALCOHOL_PER_SEK:
        return '{} ml/kr'.format(format_real(value))
    elif property_type == PropertyType.VOLUME:
        return '{} ml'.format(format_real(value))
    else:
        return value


def get_type_str(property_type: PropertyType) -> str:
    if (property_type == PropertyType.CATEGORY or
            property_type == PropertyType.PERCENTAGE or
            property_type == PropertyType.PRICE or
            property_type == PropertyType.PRICE_PER_LITER or
            property_type == PropertyType.ALCOHOL_PER_SEK or
            property_type == PropertyType.VOLUME):
        return 'INTEGER'

    return property_type.name


def create_tables(conn: sqlite3.Connection):
    expr = []
    for p in PROPERTY_TYPES_2:
        if p.type == PropertyType.CATEGORY:
            e = '{} {} DEFAULT 0 NOT NULL'.format(p.identifier, get_type_str(p.type))
        else:
            e = '{} {}'.format(p.identifier, get_type_str(p.type))

        expr.append(e)

    expr.append('PRIMARY KEY ({})'.format(first(PROPERTY_TYPES_2).identifier))

    category_tables = []
    for p in PROPERTY_TYPES_2:
        if p.type == PropertyType.CATEGORY:
            expr.append('FOREIGN KEY ({}) REFERENCES kategori_{}(ID)'
                        .format(p.identifier, p.identifier))

            category_tables.append('CREATE TABLE kategori_{} (ID INTEGER, '
                                   'Name TEXT, PRIMARY KEY (ID))'.format(p.identifier))

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
                names = property_categories.get(xml_prop.tag, ['Ospecificerad'])
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
