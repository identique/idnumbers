import re
from types import SimpleNamespace
from typing import Optional
from ..util import CHECK_DIGIT, validate_regexp, weighted_modulus_digit, modulus_overflow_mod10


class TaxIdentityNumber:
    """
    Greece Tax Identity Number, AFM - ΑΦΜ - Αριθμός Φορολογικού Μητρώου - Tax Registry Number
    https://en.wikipedia.org/wiki/National_identification_number#Greece
    """
    METADATA = SimpleNamespace(**{
        'iso3166_alpha2': 'GR',
        'min_length': 9,
        'max_length': 9,
        'parsable': False,
        'checksum': True,
        'regexp': re.compile(r'^\d{9}$'),
        'alias_of': None,
        'names': ['Tax Identity Number'],
        'links': ['https://en.wikipedia.org/wiki/National_identification_number#Greece'],
        'deprecated': False
    })

    MULTIPLIER = [256, 128, 64, 32, 16, 8, 4, 2]

    @staticmethod
    def validate(id_number: str) -> bool:
        """
        Validate with regexp
        """
        return str(TaxIdentityNumber.checksum(id_number)) == id_number[-1]

    @staticmethod
    def checksum(id_number: str) -> Optional[CHECK_DIGIT]:
        """
        ref: https://stackoverflow.com/a/4377376
        """
        if not validate_regexp(id_number, TaxIdentityNumber.METADATA.regexp):
            return None
        numbers = [int(char) for char in id_number]
        modulus = modulus_overflow_mod10(weighted_modulus_digit(numbers[0:-1], TaxIdentityNumber.MULTIPLIER, 11, True))
        return modulus
