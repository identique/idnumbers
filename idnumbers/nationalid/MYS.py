import re
from datetime import date
from types import SimpleNamespace
from typing import Optional, TypedDict
from .constant import Citizenship
from .util import validate_regexp


def normalize(id_number):
    """strip out useless characters/whitespaces"""
    return re.sub(r'-', '', id_number)


class ParseResult(TypedDict):
    """parse result for NRIC"""
    yyyymmdd: date
    """birthday"""
    location: str
    """registration location"""
    citizenship: Citizenship
    """citizenship"""
    sn: str
    """serial number"""


class NRIC:
    """
    Malaysia National ID number format, NRIC
    https://en.wikipedia.org/wiki/Malaysian_identity_card#Structure_of_the_National_Registration_Identity_Card_Number_(NRIC)
    """
    METADATA = SimpleNamespace(**{
        'iso3166_alpha2': 'MY',
        'min_length': 12,
        'max_length': 12,
        'parsable': True,
        'checksum': False,
        'regexp': re.compile(r'^(?P<yy>\d{2})(?P<mm>\d{2})(?P<dd>\d{2})-?'
                             r'(?P<pb>\d{2})-?'
                             r'(?P<sn>\d{4})$')
    })

    WRONG_PB_CODE = ['00', '17', '18', '19', '20',
                     '69', '70', '73', '80', '81', '94', '95', '96', '97']
    """black list for pb code"""

    @staticmethod
    def validate(id_number: str) -> bool:
        """
        Validate the id number
        """
        if not validate_regexp(id_number, NRIC.METADATA.regexp):
            return False
        return NRIC.parse(id_number) is not None

    @staticmethod
    def parse(id_number: str) -> Optional[ParseResult]:
        """pares the result"""
        match_obj = NRIC.METADATA.regexp.match(id_number)

        if not match_obj:
            return None
        yy = int(match_obj.group('yy'))
        mm = int(match_obj.group('mm'))
        dd = int(match_obj.group('dd'))
        location = match_obj.group('pb')
        if not NRIC.check_location_code(location):
            return None
        sn = match_obj.group('sn')
        yyyy_base = 1900 if int(sn[0]) > 4 else 2000
        try:
            return {
                'yyyymmdd': date(yyyy_base + yy, mm, dd),
                'location': location,
                'citizenship': Citizenship.CITIZEN if int(location) < 60 else Citizenship.RESIDENT,
                'sn': sn
            }
        except ValueError:
            return None

    @staticmethod
    def check_location_code(location_code: str) -> bool:
        """we use blacklist to check wrong pb code"""
        return location_code not in NRIC.WRONG_PB_CODE


NationalID = NRIC
"""alias of NRIC"""
