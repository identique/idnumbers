import re
from datetime import date
from types import SimpleNamespace
from typing import Literal, Optional, TypedDict, get_args
from .util import validate_regexp
from .constant import Gender


CHECKSUM_TYPE = Literal['0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
                        'A', 'B', 'C', 'D', 'E', 'F', 'H', 'J', 'K', 'L',
                        'M', 'N', 'P', 'R', 'S', 'T', 'U', 'V', 'W', 'X',
                        'Y']
"""literal for checksum type"""


class ParseResult(TypedDict):
    """The parse result of Finland personal identity code, HETU"""
    yyyymmdd: date
    """Birthday"""
    gender: Gender
    """Gender, male or female"""
    sn: str
    """The serial number born at the same date"""
    checksum: CHECKSUM_TYPE
    """checksum code in str"""


class PersonalIdentityCode:
    """
    Finland personal identity code, HETU
    https://en.wikipedia.org/wiki/National_identification_number#Finland
    """
    METADATA = SimpleNamespace(**{
        'iso3166_alpha2': 'FI',
        'min_length': 11,
        'max_length': 11,
        'parsable': True,
        'checksum': True,
        'regexp': re.compile(r'^(?P<dd>\d{2})(?P<mm>\d{2})(?P<yy>\d{2})'
                             r'(?P<century>[-+ABCDEFUVWXY])'
                             r'(?P<sn>\d{3})'
                             r'(?P<check>[0-9A-Z])$')
    })

    DOB_BASE_MAP = {
        '+': 1800,
        '-': 1900,
        'U': 1900,
        'V': 1900,
        'W': 1900,
        'X': 1900,
        'Y': 1900,
        'A': 2000,
        'B': 2000,
        'C': 2000,
        'D': 2000,
        'E': 2000,
        'F': 2000,
    }
    """ The century map for id """

    CHECKSUM_LIST = list(get_args(CHECKSUM_TYPE))
    """ possible checksum characteres """

    @staticmethod
    def validate(id_number: str) -> bool:
        """
        Validate the FIN id number
        """
        if not validate_regexp(id_number, PersonalIdentityCode.METADATA.regexp):
            return False
        return PersonalIdentityCode.parse(id_number) is not None

    @staticmethod
    def parse(id_number: str) -> Optional[ParseResult]:
        """ parse the FIN HETU id"""
        match_obj = PersonalIdentityCode.METADATA.regexp.match(id_number)
        if not match_obj:
            return None
        elif not PersonalIdentityCode.checksum(id_number):
            return None
        yy = int(match_obj.group('yy'))
        mm = int(match_obj.group('mm'))
        dd = int(match_obj.group('dd'))
        century = match_obj.group('century')
        sn = match_obj.group('sn')
        yyyy_base = PersonalIdentityCode.DOB_BASE_MAP[century]
        try:
            return {
                'yyyymmdd': date(yyyy_base + yy, mm, dd),
                'gender': Gender.MALE if int(sn) % 2 == 1 else Gender.FEMALE,
                'sn': sn,
                'checksum': match_obj.group('check')
            }
        except ValueError:
            return None

    @staticmethod
    def checksum(id_number: str) -> bool:
        """check if the ID valid against its checksum"""
        match_obj = PersonalIdentityCode.METADATA.regexp.match(id_number)
        if not match_obj:
            return False
        numbers = int(match_obj.group('dd') + match_obj.group('mm') + match_obj.group('yy') + match_obj.group('sn'))
        check_digit = PersonalIdentityCode.CHECKSUM_LIST[numbers % 31]
        return match_obj.group('check') == check_digit


NationalID = PersonalIdentityCode
"""alias of PersonalIdentityCode"""
HETU = PersonalIdentityCode
"""alias of PersonalIdentityCode"""
