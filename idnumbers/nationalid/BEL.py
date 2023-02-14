import re
from datetime import date
from types import SimpleNamespace
from typing import Optional, TypedDict
from .util import validate_regexp
from .constant import Gender


def normalize(id_number: str) -> str:
    """strip out useless characters/whitespaces"""
    return re.sub(r'[.-]', '', id_number)


class ParseResult(TypedDict):
    """The parse result of Belgium NationalID"""
    yyyymmdd: date
    """birthday"""
    gender: Gender
    """gender, possible value: male and female"""
    sn: str
    """serial number"""
    checksum: int
    """checksum digits, two digits"""


class NationalID:
    """
    Belgium National register number format
    https://en.wikipedia.org/wiki/Belgian_identity_card

    """
    METADATA = SimpleNamespace(**{
        'iso3166_alpha2': 'BE',
        'min_length': 11,
        'max_length': 11,
        'parsable': True,
        'checksum': True,
        'regexp': re.compile(r'^(?P<yy>\d{2})\.?(?P<mm>\d{2})\.?(?P<dd>\d{2})-?'
                             r'(?P<sn>\d{3})\.?'
                             r'(?P<checksum>\d{2})$')
    })

    @staticmethod
    def validate(id_number: str) -> bool:
        """validate the id"""
        if not validate_regexp(id_number, NationalID.METADATA.regexp):
            return False
        return NationalID.parse(id_number) is not None

    @staticmethod
    def parse(id_number: str) -> Optional[ParseResult]:
        """parse the result"""
        match_obj = NationalID.METADATA.regexp.match(id_number)
        if not match_obj:
            return None
        checksum = NationalID.checksum(id_number)
        if not checksum:
            return None
        else:
            yy = int(match_obj.group('yy'))
            mm = int(match_obj.group('mm'))
            dd = int(match_obj.group('dd'))
            sn = match_obj.group('sn')
            year_base = 1900 if yy > 50 else 2000
            try:
                return {
                    'yyyymmdd': date(yy + year_base, mm, dd),
                    'gender': Gender.MALE if int(sn) % 2 == 1 else Gender.FEMALE,
                    'sn': sn,
                    'checksum': int(match_obj.group('checksum'))
                }
            except ValueError:
                return None

    @staticmethod
    def checksum(id_number) -> bool:
        """
        calculated as the remainder of dividing xxxxxxxxxx by 97
        (if the remainder is 0, the check number is set to 97)
        """
        if not validate_regexp(id_number, NationalID.METADATA.regexp):
            return False
        normalized = normalize(id_number)
        check_digits = normalized[-2:]
        if int(normalized[0:2]) < 50:
            # the person should be born after 2000
            check = 97 - (2000000000 + int(normalized[:-2])) % 97
        else:
            check = 97 - int(normalized[:-2]) % 97

        return int(check_digits) == check
