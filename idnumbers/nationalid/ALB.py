import re
from datetime import date
from types import SimpleNamespace
from typing import Literal, Optional, TypedDict
from .constant import Gender


class ParseResult(TypedDict):
    """Parse result of id number"""
    yyyymmdd: date
    """year of birth"""
    sn: str
    """serial number"""
    gender: Gender
    """gender: male or female"""
    checksum: Literal['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K',
                      'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'Y', 'U',
                      'V', 'W']  # cannot use CHECK_ALPHA because it ends with W
    """check digits"""


class IdentityNumber:
    """
    Albania Identity Number, Numri i Identitetit (NID),  Numri i Identitetit të Shtetasit (NISH), NIPT
    https://en.wikipedia.org/wiki/National_identification_number#Albania
    """
    METADATA = SimpleNamespace(**{
        'iso3166_alpha2': 'AL',
        'min_length': 10,
        'max_length': 10,
        'parsable': True,
        'checksum': False,  # There is a checksum algorithm. But we cannot find it.
        'regexp': re.compile(r'^(?P<yy>[0-9A-T]\d)(?P<mm>\d{2})(?P<dd>\d{2})'
                             r'(?P<sn>\d{3})[ -]?'
                             r'(?P<checksum>[A-W])$')
    })

    BASE_YEAR_MAP = '0123456789ABCDEFGHIJKLMNOPQRST'

    @staticmethod
    def validate(id_number: str) -> bool:
        """
        Validate the id number
        """
        if not id_number:
            return False

        if not isinstance(id_number, str):
            id_number = repr(id_number)
        return IdentityNumber.parse(id_number) is not None

    @staticmethod
    def parse(id_number: str) -> Optional[ParseResult]:
        """parse the result"""
        match_obj = IdentityNumber.METADATA.regexp.match(id_number)
        if not match_obj:
            return None
        yyyy = IdentityNumber.get_year(match_obj.group('yy'))
        mm = int(match_obj.group('mm'))
        dd = int(match_obj.group('dd'))
        try:
            return {
                'yyyymmdd': date(yyyy, mm if mm < 50 else mm - 50, dd),
                'gender': Gender.MALE if mm < 50 else Gender.FEMALE,
                'sn': match_obj.group('sn'),
                'checksum': match_obj.group('checksum')
            }
        except ValueError:
            return None

    @staticmethod
    def get_year(yy: str) -> int:
        year_base = 1800 + IdentityNumber.BASE_YEAR_MAP.index(yy[0]) * 10
        return year_base + int(yy[1])


NationalID = IdentityNumber
"""alias of IdentityNumber"""
NISH = IdentityNumber
"""alias of IdentityNumber"""
NIPT = IdentityNumber
"""alias of IdentityNumber"""
NID = IdentityNumber
"""alias of IdentityNumber"""
