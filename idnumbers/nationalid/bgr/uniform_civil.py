import re
from datetime import date
from types import SimpleNamespace
from typing import TypedDict, Optional, cast

from ..util import validate_regexp, CHECK_DIGIT, weighted_modulus_digit, match_regexp
from ..constant import Gender


class ParseResult(TypedDict):
    """Parse result of UniformCivilNumber"""
    yyyymmdd: date
    """birthday"""
    checksum: CHECK_DIGIT
    """check digits"""
    gender: Gender
    """gender: male/female"""


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
                             r'(?P<checksum>\d)$'),
        'alias_of': None,
        'names': ['Uniform civil number',
                  'Единен граждански номер',
                  'Edinen grazhdanski nomer',
                  'ЕГН',
                  'EGN'],
        'links': ['https://en.wikipedia.org/wiki/National_identification_number#Bulgaria',
                  'https://en.wikipedia.org/wiki/Unique_citizenship_number',
                  'https://github.com/arthurdejong/python-stdnum/blob/master/stdnum/bg/egn.py'],
        'deprecated': False
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
        match_obj = match_regexp(id_number, UniformCivilNumber.METADATA.regexp)
        if match_obj is None:
            return None
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
                "checksum": cast(CHECK_DIGIT, int(checksum)),
                'gender': Gender.MALE if int(match_obj.group("gender")) % 2 == 0 else Gender.FEMALE
            }
        except ValueError:
            return None

    MULTIPLIER = [2, 4, 8, 5, 10, 9, 7, 3, 6]

    @staticmethod
    def checksum(id_number: str) -> Optional[CHECK_DIGIT]:
        """
        Get the checksum digit, or None when the input is not a well-formed BGR id number

        The check digit is the weighted sum of the first nine digits (weights 2, 4, 8, 5, 10, 9, 7, 3, 6)
        modulo 11. When that remainder is 10 the check digit is 0, so the result is always 0..9.

        Sources:
        https://en.wikipedia.org/wiki/Unique_citizenship_number ("If the result is 10, the check digit becomes 0")
        https://github.com/arthurdejong/python-stdnum/blob/master/stdnum/bg/egn.py (calc_check_digit: sum % 11 % 10)
        """
        if not validate_regexp(id_number, UniformCivilNumber.METADATA.regexp):
            return None
        digits_numbers = [int(i) for i in id_number[:-1]]
        remainder = weighted_modulus_digit(digits_numbers, UniformCivilNumber.MULTIPLIER, 11, True)
        return cast(CHECK_DIGIT, remainder % 10)
