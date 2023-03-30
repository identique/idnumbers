import re
from datetime import date
from types import SimpleNamespace
from typing import Literal, Optional, TypedDict
from ..util import validate_regexp
from ..constant import Citizenship, Gender


class ParseResult(TypedDict):
    """parse result for national id"""
    yyyymmdd: date
    """birthday"""
    gender: Gender
    """gender, possible value: male, female"""
    citizenship: Citizenship
    """citizenship"""
    sn: str
    """serial number if two persons born on the same date"""


class OldIDParseResult(ParseResult):
    """Old format contains more information"""
    location: str
    """registration location"""
    checksum: Literal[0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    """check digits"""


class ResidentRegistration:
    """
    KOR resident registration number format. The ARC is the same as ResidentRegistration. KOR removed the checksum and location
    from Oct. 2020 to protect privacy.
    # https://en.wikipedia.org/wiki/Resident_registration_number
    # https://centers.ibs.re.kr/html/living_en/overview/arc.html
    """
    METADATA = SimpleNamespace(**{
        'iso3166_alpha2': 'KR',
        'min_length': 13,
        'max_length': 13,
        'parsable': True,
        'checksum': False,
        'regexp': re.compile(r'^(?P<yy>\d{2})(?P<mm>\d{2})(?P<dd>\d{2})-'
                             r'(?P<gender>\d)'
                             r'(?P<sn>\d{6})$'),
        'alias_of': None,
        'names': ['Resident Registration Number',
                  '주민등록번호',
                  'RRN',
                  '住民登錄番號',
                  'Jumin Deungnok Beonho'],
        'links': ['https://en.wikipedia.org/wiki/Resident_registration_number',
                  'https://centers.ibs.re.kr/html/living_en/overview/arc.html'],
        'deprecated': False
    })

    CITIZENSHIP_MAP = {
        9: Citizenship.CITIZEN,
        0: Citizenship.CITIZEN,
        1: Citizenship.CITIZEN,
        2: Citizenship.CITIZEN,
        3: Citizenship.CITIZEN,
        4: Citizenship.CITIZEN,
        5: Citizenship.RESIDENT,
        6: Citizenship.RESIDENT,
        7: Citizenship.RESIDENT,
        8: Citizenship.RESIDENT
    }
    """citizenship map"""

    DOB_BASE_MAP = {
        9: 1800,
        0: 1800,
        1: 1900,
        2: 1900,
        3: 2000,
        4: 2000,
        5: 1900,
        6: 1900,
        7: 2000,
        8: 2000
    }
    """dob base year map"""

    @staticmethod
    def validate(id_number: str) -> bool:
        """
        Validate the KOR id number
        """
        if not validate_regexp(id_number, ResidentRegistration.METADATA.regexp):
            return False
        return ResidentRegistration.parse(id_number) is not None

    @staticmethod
    def parse(id_number: str) -> Optional[ParseResult]:
        """parse the result"""
        match_obj = ResidentRegistration.METADATA.regexp.match(id_number)
        return ResidentRegistration.build_parse_result(match_obj)

    @staticmethod
    def build_parse_result(match_obj: re.Match[str]) -> Optional[ParseResult]:
        if not match_obj:
            return None
        yy = int(match_obj.group('yy'))
        mm = int(match_obj.group('mm'))
        dd = int(match_obj.group('dd'))
        gender = int(match_obj.group('gender'))
        sn = match_obj.group('sn')
        yyyy_base = ResidentRegistration.DOB_BASE_MAP[gender]
        try:
            return {
                'yyyymmdd': date(yyyy_base + yy, mm, dd),
                'gender': Gender.MALE if gender % 2 == 1 else Gender.FEMALE,
                'citizenship': ResidentRegistration.CITIZENSHIP_MAP[gender],
                'sn': sn
            }
        except ValueError:
            return None
