import re
from types import SimpleNamespace
from .util import validate_regexp, weighted_modulus_digit


def normalize(id_number):
    """strip out useless characters/whitespaces"""
    return re.sub(r'[-.]', '', id_number)


class NationalID:
    """
    CHL national ID number format
    https://en.wikipedia.org/wiki/National_identification_number#Canada
    """
    METADATA = SimpleNamespace(**{
        'iso3166_alpha2': 'CL',
        # length without insignificant chars
        'min_length': 8,
        'max_length': 9,
        # has parse function
        'parsable': False,
        # has checksum function
        'checksum': True,
        # regular expression to validate the id
        'regexp': re.compile(r'^(\d{1,2}[.]\d{3}[.]\d{3}-[\d|K])$')
    })

    @staticmethod
    def validate(id_number: str) -> bool:
        """
        Validate the CHL id number
        https://codepen.io/alisteroz/pen/KEoqgQ
        """
        if not validate_regexp(id_number, NationalID.METADATA.regexp):
            return False
        return NationalID.checksum(id_number) == id_number[-1]

    @staticmethod
    def checksum(id_number: str) -> str:
        """
        Validate CHL national id number checksum
        https://gist.github.com/ryangreenberg/4531891
        """
        MOD = 11
        MULTIPLIER = [3, 2, 7, 6, 5, 4, 3, 2]
        number_list = [int(char) for char in list(normalize(id_number)[:-1])]
        modulus = weighted_modulus_digit(number_list, MULTIPLIER, MOD)
        return str(0 if modulus == 11 else 'K' if modulus == 10 else modulus)
