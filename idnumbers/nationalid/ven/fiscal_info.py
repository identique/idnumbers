import re
from types import SimpleNamespace

from ..util import validate_regexp, weighted_modulus_digit


def normalize(id_number):
    """strip out useless characters/whitespaces"""
    return re.sub(r'[ \-.]', '', id_number)


class FiscalInformationNumber:
    """
    Venezuela RIF (Fiscal Information Registry) number, Registro de Informacion Fiscal
    https://en.wikipedia.org/wiki/National_identification_number#Venezuela
    python version of
    https://github.com/anghelvalentin/CountryValidator/blob/master/CountryValidator/CountriesValidators/VenezuelaAfricaValidator.cs
    """
    METADATA = SimpleNamespace(**{
        'iso3166_alpha2': 'VE',
        # length without insignificant chars
        'min_length': 10,
        'max_length': 10,
        # has parse function
        'parsable': False,
        # has checksum function
        'checksum': True,
        # regular expression to validate the id
        'regexp': re.compile(r'^[VEJPG]-?\d{8}-?\d$'),
        'alias_of': None,
        'names': ['Fiscal Information Number',
                  'RIF',
                  'Registro de Informacion Fiscal'],
        'links': ['https://en.wikipedia.org/wiki/National_identification_number#Venezuela'],
        'deprecated': False
    })

    WEIGHTS = [1, 3, 2, 7, 6, 5, 4, 3, 2]
    TYPE_MAP = {
        'V': 4,
        'E': 8,
        'J': 12,
        'P': 16,
        'G': 20
    }

    @staticmethod
    def validate(id_number: str) -> bool:
        """
        Validate
        """
        return FiscalInformationNumber.checksum(id_number)

    @staticmethod
    def checksum(id_number: str) -> bool:
        """algorithm: https://github.com/therezor/ua-tax-number/blob/main/src/Decoder.php"""
        if not validate_regexp(id_number, FiscalInformationNumber.METADATA.regexp):
            return False
        normalized = normalize(id_number)
        numbers = [FiscalInformationNumber.TYPE_MAP[normalized[0]]] + [int(char) for char in list(normalized[1:])]
        modulus = weighted_modulus_digit(numbers[:-1], FiscalInformationNumber.WEIGHTS, 11)
        modulus = modulus if modulus < 10 else 0
        return modulus == numbers[-1]


RIF = FiscalInformationNumber
"""alias of FiscalInformationNumber"""
