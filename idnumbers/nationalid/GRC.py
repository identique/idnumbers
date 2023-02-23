import re
from types import SimpleNamespace
from .util import validate_regexp, weighted_modulus_digit, modulus_overflow_mod10


class OldIdentityCard:
    """
    Greece Identity Card, the old one.
    https://en.wikipedia.org/wiki/National_identification_number#Greece
    """
    METADATA = SimpleNamespace(**{
        'iso3166_alpha2': 'GR',
        'min_length': 7,
        'max_length': 7,
        'parsable': False,
        'checksum': False,
        'regexp': re.compile(r'^[ΑΒΓΔΕΖΗΘΙΚΛΜΝΞΟΠΡΣΤΥΦΧΨΩ]-?\d{6}$')
    })

    @staticmethod
    def validate(id_number: str) -> bool:
        """
        Validate with regexp
        """
        return validate_regexp(id_number, OldIdentityCard.METADATA.regexp)


class IdentityCard:
    """
    Greece Identity Card, the new one.
    https://en.wikipedia.org/wiki/National_identification_number#Greece
    """
    METADATA = SimpleNamespace(**{
        'iso3166_alpha2': 'GR',
        'min_length': 7,
        'max_length': 7,
        'parsable': False,
        'checksum': False,
        'regexp': re.compile(r'^[ΑΒΓΔΕΖΗΘΙΚΛΜΝΞΟΠΡΣΤΥΦΧΨΩABEZHIKMNOPTYX]{2}-?\d{6}$')
        # They are two different char set, the former is Greek alphabet, the latter is Latin alphabet
    })

    @staticmethod
    def validate(id_number: str) -> bool:
        """
        Validate with regexp
        """
        return validate_regexp(id_number, IdentityCard.METADATA.regexp)


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
        'regexp': re.compile(r'^\d{9}$')
    })

    MULTIPLIER = [256, 128, 64, 32, 16, 8, 4, 2]

    @staticmethod
    def validate(id_number: str) -> bool:
        """
        Validate with regexp
        """
        return TaxIdentityNumber.checksum(id_number)

    @staticmethod
    def checksum(id_number: str) -> bool:
        """
        ref: https://stackoverflow.com/a/4377376
        """
        if not validate_regexp(id_number, TaxIdentityNumber.METADATA.regexp):
            return False
        numbers = [int(char) for char in id_number]
        modulus = modulus_overflow_mod10(weighted_modulus_digit(numbers[0:-1], TaxIdentityNumber.MULTIPLIER, 11, True))
        return numbers[-1] == modulus


NationalID = IdentityCard
"""
alias of IdentityCard
"""
