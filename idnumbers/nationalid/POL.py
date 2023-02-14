import re
from datetime import date
from types import SimpleNamespace
from typing import Optional, Tuple, TypedDict
from .util import CHECK_DIGIT, modulus_overflow_mod10, validate_regexp, weighted_modulus_digit
from .constant import Gender


YEAR_MONTH_TYPE = Tuple[int, int]


class ParseResult(TypedDict):
    yyyymmdd: date
    """birthday of this ID"""
    gender: Gender
    """only male or female"""
    sn: str
    """serial number"""
    checksum: CHECK_DIGIT
    """checksum digit"""


class PESEL:
    """
    Poland PESEL code
    https://en.wikipedia.org/wiki/PESEL
    https://en.wikipedia.org/wiki/National_identification_number#Poland
    """
    METADATA = SimpleNamespace(**{
        'iso3166_alpha2': 'PL',
        'min_length': 11,
        'max_length': 11,
        'parsable': True,
        'checksum': True,
        'regexp': re.compile(r'^(?P<yy>\d{2})'
                             r'(?P<mm>\d{2})'
                             r'(?P<dd>\d{2})'
                             r'(?P<sn>\d{4})'
                             r'(?P<checksum>\d)$')
    })

    MAGIC_NUMBERS = [1, 3, 7, 9, 1, 3, 7, 9, 1, 3]

    @staticmethod
    def validate(id_number: str) -> bool:
        """
        Validate the Poland PESEL code
        """
        if not id_number:
            return False

        if not isinstance(id_number, str):
            id_number = repr(id_number)
        return PESEL.parse(id_number) is not None

    @staticmethod
    def parse(id_number: str) -> Optional[ParseResult]:
        """
        parse the id number
        """
        match_obj = PESEL.METADATA.regexp.match(id_number)
        if not match_obj:
            return None

        checksum = PESEL.checksum(id_number)
        if checksum is None or str(checksum) != match_obj.group('checksum'):
            return None

        yy = int(match_obj.group('yy'))
        mm_coded = int(match_obj.group('mm'))
        dd = int(match_obj.group('dd'))
        year_base, mm = PESEL.get_year_base_month(mm_coded)
        sn = match_obj.group('sn')
        try:
            return {
                'yyyymmdd': date(year_base + yy, mm, dd),
                'gender': Gender.MALE if int(sn[-1]) % 2 == 1 else Gender.FEMALE,
                'sn': sn,
                'checksum': checksum
            }
        except ValueError:
            return None

    @staticmethod
    def get_year_base_month(month: int) -> YEAR_MONTH_TYPE:
        """ from https://en.wikipedia.org/wiki/PESEL#Birthdates """
        if month > 80:
            return 1800, month - 80
        elif month > 60:
            return 2200, month - 60
        elif month > 40:
            return 2100, month - 40
        elif month > 20:
            return 2000, month - 20
        else:
            return 1900, month

    @staticmethod
    def checksum(id_number) -> Optional[CHECK_DIGIT]:
        """
        python implementation of https://en.wikipedia.org/wiki/PESEL#Checksum_calculation
        """
        if not validate_regexp(id_number, PESEL.METADATA.regexp):
            return None
        numbers = [int(char) for char in id_number[:-1]]
        return modulus_overflow_mod10(weighted_modulus_digit(numbers, PESEL.MAGIC_NUMBERS, 10))


NationalID = PESEL
"""alias of PESEL"""
