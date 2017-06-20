from enum import Enum


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
    'Ros\u00e9': 'roseviner'}


def get_property_by_identifier(identifier: str) -> SystembolagetProperty:
    for p in PROPERTY_TYPES_2:
        if identifier == p.identifier:
            return p

    return None


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
