import re
from types import SimpleNamespace
from typing import Optional
from .util import CHECK_DIGIT, validate_regexp, weighted_modulus_digit, letter_to_number


def normalize(id_number: str) -> str:
    """strip out useless characters/whitespaces"""
    return id_number.replace('-', '')


class NationalID:
    """
    Iran national id number, (کارت ملی/kart-e-meli)
    https://en.wikipedia.org/wiki/National_identification_number#Iran,_Islamic_Republic_of
    """
    METADATA = SimpleNamespace(**{
        'iso3166_alpha2': 'IR',
        'min_length': 10,
        'max_length': 10,
        'parsable': False,
        'checksum': True,
        'regexp': re.compile(r'^\d{3}-?\d{6}-?\d$')
    })

    MULTIPLIER = [10, 9, 8, 7, 6, 5, 4, 3, 2]

    @staticmethod
    def validate(id_number: str) -> bool:
        """
        Validate
        """
        if not validate_regexp(id_number, NationalID.METADATA.regexp):
            return False
        return NationalID.checksum(id_number) == int(id_number[-1])

    @staticmethod
    def checksum(id_number: str) -> Optional[CHECK_DIGIT]:
        """algorithm: https://github.com/mohammadv184/idvalidator/blob/main/validate/nationalid/nationalid.go"""
        normalized = normalize(id_number)
        numbers = [int(i) for i in normalized]
        modulus = weighted_modulus_digit(numbers[:-1], NationalID.MULTIPLIER, 11, True)
        return modulus if modulus < 2 else 11 - modulus
