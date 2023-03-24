import re
from enum import Enum
from types import SimpleNamespace
from typing import TypedDict, Optional

from .util import validate_regexp


class ResidentialType(Enum):
    RURAL = 1
    MUNICIPALITY = 2
    CITY = 3
    OTHERS = 4
    CANTONMENT = 5
    CITY_CORPORATION = 9


class OldParseResult(TypedDict):
    distinct: str
    """distinct code"""
    residential_type: ResidentialType
    """RMO/residential type"""
    policy_station_no: str
    """upazilla/ thana/police station number"""
    union_code: str
    """your union code/ward number"""
    sn: str
    """serial no"""


class ParseResult(OldParseResult):
    yyyy: str
    """birth year"""


class OldNationalID:
    """
    Bangladesh National ID number, জাতীয় পরিচয়পত্র, NID, BD
    https://en.wikipedia.org/wiki/National_identity_card_(Bangladesh)
    http://nationalidcardbangladesh.blogspot.com/2016/04/voter-id-national-id-card-number.html
    https://www.facebook.com/428195627559147/photos/a.428251897553520/428251617553548/?type=3
    """
    METADATA = SimpleNamespace(**{
        'iso3166_alpha2': 'BD',
        # length without insignificant chars
        'min_length': 13,
        'max_length': 13,
        'parsable': True,
        'checksum': False,
        'regexp': re.compile(r'^(?P<distinct>\d{2})'
                             r'(?P<rmo>\d)'
                             r'(?P<police>\d{2})'
                             r'(?P<union>\d{2})'
                             r'(?P<sn>\d{6})$')
    })

    RMO_MAP = {
        '1': ResidentialType.RURAL,
        '2': ResidentialType.MUNICIPALITY,
        '3': ResidentialType.CITY,
        '4': ResidentialType.OTHERS,
        '5': ResidentialType.CANTONMENT,
        '9': ResidentialType.CITY_CORPORATION
    }

    @staticmethod
    def validate(id_number: str) -> bool:
        """
        Validate
        """
        if not validate_regexp(id_number, OldNationalID.METADATA.regexp):
            return False
        return OldNationalID.parse(id_number) is not None

    @staticmethod
    def parse(id_number: str) -> Optional[OldParseResult]:
        """
        Parse the result
        """
        match_obj = OldNationalID.METADATA.regexp.match(id_number)
        if not match_obj:
            return None

        if match_obj.group('rmo') not in OldNationalID.RMO_MAP:
            return None

        try:
            return {
                'distinct': match_obj.group('distinct'),
                'residential_type': OldNationalID.RMO_MAP[match_obj.group('rmo')],
                'policy_station_no': match_obj.group('police'),
                'union_code': match_obj.group('union'),
                'sn': match_obj.group('sn')
            }
        except ValueError:
            return None


class NationalID(OldNationalID):
    """
    Bangladesh National ID number, জাতীয় পরিচয়পত্র, NID, BD
    https://en.wikipedia.org/wiki/National_identity_card_(Bangladesh)
    http://nationalidcardbangladesh.blogspot.com/2016/04/voter-id-national-id-card-number.html
    https://www.facebook.com/428195627559147/photos/a.428251897553520/428251617553548/?type=3
    """
    METADATA = SimpleNamespace(**{
        'iso3166_alpha2': 'BD',
        # length without insignificant chars
        'min_length': 13,
        'max_length': 13,
        'parsable': True,
        'checksum': False,
        'regexp': re.compile(r'^(?P<yyyy>\d{4})'
                             r'(?P<distinct>\d{2})'
                             r'(?P<rmo>\d)'
                             r'(?P<police>\d{2})'
                             r'(?P<union>\d{2})'
                             r'(?P<sn>\d{6})$')
    })

    @staticmethod
    def validate(id_number: str) -> bool:
        """
        Validate
        """
        if not validate_regexp(id_number, NationalID.METADATA.regexp):
            return False
        return NationalID.parse(id_number) is not None

    @staticmethod
    def parse(id_number: str) -> Optional[ParseResult]:
        """
        Parse the result
        """
        match_obj = NationalID.METADATA.regexp.match(id_number)
        if not match_obj:
            return None
        old_result = OldNationalID.parse(id_number[4:])
        if not old_result:
            return None
        return {
            **old_result,
            'yyyy': int(id_number[0:4])
        }
