import re
from types import SimpleNamespace
from typing import Optional, TypedDict
from .util import validate_regexp
from .constant import Gender


class ParseResult(TypedDict):
    """The parse result of Pakistan ID"""
    location: str
    """registration location"""
    sn: str
    """serial number"""
    gender: Gender
    """gender: male or female"""


class NationalID:
    """
    Pakistan National ID Card number format, CNIC, NIC, قومی شناختی کارڈ
    https://en.wikipedia.org/wiki/National_identification_number#Pakistan
    https://en.wikipedia.org/wiki/CNIC_(Pakistan)#Security_features
    https://www.geo.tv/latest/250118-mystery-behind-13-digit-cnic-number
    https://www.informationpk.com/interesting-information-about-or-meaning-of-nadra-cnic-13-digits-number/
    check website: https://cnic.com.pk/
    """
    METADATA = SimpleNamespace(**{
        'iso3166_alpha2': 'PA',
        'min_length': 13,
        'max_length': 13,
        'parsable': True,
        'checksum': False,
        'regexp': re.compile(r'^(?P<location>\d{5})-?'
                             r'(?P<sn>\d{7})-?'
                             r'(?P<gender>\d)$')
    })
    """metadata of this id"""

    @staticmethod
    def validate(id_number: str) -> bool:
        """validate"""
        if not validate_regexp(id_number, NationalID.METADATA.regexp):
            return False
        return NationalID.parse(id_number) is not None

    @staticmethod
    def parse(id_number: str) -> Optional[ParseResult]:
        """parse the result"""
        match_obj = NationalID.METADATA.regexp.match(id_number)
        if not match_obj:
            return None
        try:
            return {
                'location': match_obj.group('location'),
                'sn': match_obj.group('sn'),
                'gender': Gender.MALE if int(match_obj.group('gender')) % 2 == 1 else Gender.FEMALE,
            }
        except ValueError:
            # catch the date error
            return None


CNIC = NationalID
"""alias of NationalID"""
