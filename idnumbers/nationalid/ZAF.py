import re
from datetime import date
from typing import Optional, TypedDict
from types import SimpleNamespace
from .constant import Citizenship, Gender
from .util import CHECK_DIGIT, luhn_digit


class ParseResult(TypedDict):
    """parse result of national id"""
    yyyymmdd: date
    """birthday"""
    sn: str
    """serial number"""
    gender: Gender
    """gender, possible value: male, female"""
    citizenship: Citizenship
    """citizenship"""
    checksum: CHECK_DIGIT
    """check digit"""


class NationalID:
    """
    South Africa national ID number format
    https://en.wikipedia.org/wiki/National_identification_number#South_Africa
    https://www.westerncape.gov.za/general-publication/decoding-your-south-african-id-number-0
    """
    METADATA = SimpleNamespace(**{
        'iso3166_alpha2': 'ZA',
        # length without insignificant chars
        'min_length': 13,
        'max_length': 13,
        # has parse function
        'parsable': True,
        # has checksum function
        'checksum': True,
        # regular expression to validate the id
        'regexp': re.compile(r'^(?P<yy>\d{2})(?P<mm>0[1-9]|1[12])'
                             r'(?P<dd>0[1-9]|[12][0-9]|3[01])'
                             r'(?P<sn>\d{4})'
                             r'(?P<citizenship>[01])([89])'
                             r'(?P<checksum>\d)$')
    })

    @staticmethod
    def validate(id_number: str) -> bool:
        """
        Validate the ZAF id number
        """
        if not isinstance(id_number, str):
            id_number = repr(id_number)
        return NationalID.parse(id_number) is not None

    @staticmethod
    def parse(id_number: str) -> Optional[ParseResult]:
        match_obj = NationalID.METADATA.regexp.match(id_number)
        check_digit = NationalID.checksum(id_number)
        if not match_obj:
            return None
        elif check_digit != int(id_number[-1:]):
            return None

        year = int(match_obj.group('yy'))
        year += 2000 if year < 50 else 1900
        try:
            return {
                'yyyymmdd': date(year, int(match_obj.group('mm')), int(match_obj.group('dd'))),
                'sn': match_obj.group('sn'),
                'gender': Gender.MALE if int(match_obj.group('sn')[0]) > 4 else Gender.FEMALE,
                'citizenship': Citizenship.CITIZEN if match_obj.group('citizenship') == '0' else Citizenship.RESIDENT,
                'checksum': check_digit
            }
        except ValueError:
            return None

    @staticmethod
    def checksum(id_number: str) -> CHECK_DIGIT:
        """
        use Luhn algorithm.
        """
        return luhn_digit([int(char) for char in id_number[:-1]])
