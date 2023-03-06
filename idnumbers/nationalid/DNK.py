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
    sn: str
    """The serial number born at the same date"""


class PersonalIdentityNumber:
    """
    Denmark personal identity number, CPR, Det Centrale Personregister
    https://en.wikipedia.org/wiki/National_identification_number#Denmark
    """
    METADATA = SimpleNamespace(**{
        'iso3166_alpha2': 'DK',
        'min_length': 10,
        'max_length': 10,
        'parsable': True,
        'checksum': False,
        'regexp': re.compile(r'^(?P<dd>\d{2})(?P<mm>\d{2})(?P<yy>\d{2})-?'
                             r'(?P<sn>\d{4})$')
    })

    @staticmethod
    def validate(id_number: str) -> bool:
        """
        Validate the id number
        """
        if not validate_regexp(id_number, PersonalIdentityNumber.METADATA.regexp):
            return False
        return PersonalIdentityNumber.parse(id_number) is not None

    @staticmethod
    def parse(id_number: str) -> Optional[ParseResult]:
        """ parse the CPR id"""
        match_obj = PersonalIdentityNumber.METADATA.regexp.match(id_number)
        if not match_obj:
            return None
        yy = int(match_obj.group('yy'))
        mm = int(match_obj.group('mm'))
        dd = int(match_obj.group('dd'))
        sn = match_obj.group('sn')
        yyyy_base = 1900 if yy > 50 else 2000
        try:
            return {
                'yyyymmdd': date(yyyy_base + yy, mm, dd),
                'sn': sn
            }
        except ValueError:
            return None


NationalID = PersonalIdentityNumber
"""alias of PersonalIdentityNumber"""
CPR = PersonalIdentityNumber
"""alias of PersonalIdentityNumber"""
