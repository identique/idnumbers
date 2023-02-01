import re
from types import SimpleNamespace

from .util import validate_regexp, mn_modulus_digit, modulus_overflow_mod10


class PersonalID:
    """
    Croatia Personal ID number format, OIB
    https://en.wikipedia.org/wiki/Personal_identification_number_(Croatia)
    """
    METADATA = SimpleNamespace(**{
        'iso3166_alpha2': 'HR',
        'min_length': 11,
        'max_length': 11,
        'parsable': False,
        'checksum': True,
        'regexp': re.compile(r"^\d{11}$")
    })

    @staticmethod
    def validate(id_number: str) -> bool:
        """
        Validate HRV id number
        """
        if not validate_regexp(id_number, PersonalID.METADATA.regexp):
            return False
        return PersonalID.checksum(id_number)

    @staticmethod
    def checksum(id_number: str) -> bool:
        """
        Calculate HRV personal id checksum digit
        """
        numbers = [int(char) for char in id_number]
        checksum = modulus_overflow_mod10(mn_modulus_digit(numbers[:-1], 10, 11))
        return numbers[-1] == checksum


OIB = PersonalID
"""
alias of PersonalID
"""

NationalID = PersonalID
"""
alias of PersonalID
"""
