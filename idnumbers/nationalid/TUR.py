import re
from types import SimpleNamespace
from .util import validate_regexp, weighted_modulus_digit


class NationalID:
    """
    Turkey National ID number
    https://en.wikipedia.org/wiki/National_identification_number#Turkey
    https://stackoverflow.com/questions/53610208/turkish-identity-number-verification
    """
    METADATA = SimpleNamespace(**{
        'iso3166_alpha2': 'TR',
        # length without insignificant chars
        'min_length': 11,
        'max_length': 11,
        'parsable': False,
        'checksum': True,
        'regexp': re.compile(r'^[1-9]\d{10}$')
    })

    MULTIPLIERS = [7, -1, 7, -1, 7, -1, 7, -1, 7]
    """multiplier for the checksum"""

    @staticmethod
    def validate(id_number: str) -> bool:
        """
        Validate TUR national id number
        """
        if not validate_regexp(id_number, NationalID.METADATA.regexp):
            return False
        return NationalID.checksum(id_number) == id_number[-2:]

    @staticmethod
    def checksum(id_number: str) -> str:
        """
        Calculate the checksum e.g. digit 10 and digit 11
        """
        numbers_list = [int(i) for i in id_number]
        digit_ten = weighted_modulus_digit(numbers_list[:-2], NationalID.MULTIPLIERS, 10, True)
        digit_eleven = sum(numbers_list[:-1]) % 10
        return f'{digit_ten}{digit_eleven}'
