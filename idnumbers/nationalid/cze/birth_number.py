from copy import copy
from ..svk.birth_number import BirthNumber as __SVKBirthNumber


CZE_METADATA = copy(__SVKBirthNumber.METADATA)
CZE_METADATA.iso3166_alpha2 = 'CZ'
CZE_METADATA.links = ['https://en.wikipedia.org/wiki/National_identification_number#Czech_Republic_and_Slovakia',
                      'https://cs.wikipedia.org/wiki/Rodn%C3%A9_%C4%8D%C3%ADslo',
                      'https://github.com/arthurdejong/python-stdnum/blob/master/stdnum/cz/rc.py']
CZE_METADATA.country_name = 'Czechia'
CZE_METADATA.id_type = 'Birth Number'
CZE_METADATA.official_name = 'rodné číslo'
CZE_METADATA.display_format = 'YYMMDD/SSSC'
CZE_METADATA.example = '000101/0009'
CZE_METADATA.checksum_algorithm = 'The whole 10-digit number is divisible by 11 (a 9-digit number has no check digit)'
CZE_METADATA.masks = ('######/####', '######/###')


class BirthNumber(__SVKBirthNumber):
    """
    Czech Republic uses the same system of SVK. Birth Number (Czech/Slovak: rodné číslo (RČ))
    https://en.wikipedia.org/wiki/National_identification_number#Czech_Republic_and_Slovakia
    """
    METADATA = CZE_METADATA
