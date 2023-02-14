import re
from datetime import date
from types import SimpleNamespace
from typing import TypedDict, Optional

from .util import validate_regexp, CHECK_DIGIT, weighted_modulus_digit
from .constant import Gender


class ParseResult(TypedDict):
    """Parse result of UniformCivilNumber"""
    yyyymmdd: date
    """year of birth"""
    checksum: CHECK_DIGIT
    """check digits"""
    gender: Gender


class UniformCivilNumber:
    """
    Bulgaria Uniform civil number
    https://en.wikipedia.org/wiki/National_identification_number#Bulgaria
    """
    METADATA = SimpleNamespace(**{
        'iso3166_alpha2': 'BG',
        # length without insignificant chars
        'min_length': 10,
        'max_length': 10,
        'parsable': True,
        'checksum': True,
        'regexp': re.compile(r'^(?P<yy>\d{2})'
                             r'(?P<mm>\d{2})'
                             r'(?P<dd>\d{2})'
                             r'\d{2}'
                             r'(?P<gender>\d)'
                             r'(?P<checksum>\d)$')
    })

    @staticmethod
    def validate(id_number: str) -> bool:
        """
        Validate the BGR id number
        """
        if not validate_regexp(id_number, UniformCivilNumber.METADATA.regexp):
            return False
        return UniformCivilNumber.parse(id_number) is not None

    @staticmethod
    def parse(id_number: str) -> Optional[ParseResult]:
        """
        Parse the result
        """
        match_obj = UniformCivilNumber.METADATA.regexp.match(id_number)
        checksum = int(match_obj.group("checksum"))
        yy = int(match_obj.group("yy"))
        mm = int(match_obj.group("mm"))
        dd = int(match_obj.group("dd"))
        if UniformCivilNumber.checksum(id_number) != checksum:
            return None
        if mm > 40:
            mm -= 40
            yyyy = yy + 2000
        elif mm > 20:
            mm -= 20
            yyyy = yy + 1800
        else:
            yyyy = yy + 1900
        try:
            return {
                'yyyymmdd': date(yyyy, mm, dd),
                "checksum": int(checksum),
                'gender': Gender.MALE if int(match_obj.group("gender")) % 2 == 0 else Gender.FEMALE
            }
        except ValueError:
            return None

    MULTIPLIER = [2, 4, 8, 5, 10, 9, 7, 3, 6]

    @staticmethod
    def checksum(id_number: str) -> CHECK_DIGIT:
        """
        Get the checksum digit
        https://en.wikipedia.org/wiki/Unique_citizenship_number
        """
        digits_numbers = [int(i) for i in id_number[:-1]]
        return weighted_modulus_digit(digits_numbers, UniformCivilNumber.MULTIPLIER, 11, True)
