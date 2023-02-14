import re
from datetime import date
from types import SimpleNamespace
from typing import Literal, Optional, TypedDict
from .util import weighted_modulus_digit, modulus_overflow_mod10, validate_regexp
from .constant import Citizenship, Gender


def normalize(id_number):
    """strip out useless characters/whitespaces"""
    return re.sub(r'-', '', id_number)


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


class NationalID:
    """
    KOR National ID number format. The ARC is the same as NationalID. KOR removed the checksum and location
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
                             r'(?P<sn>\d{6})$')
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
        if not validate_regexp(id_number, NationalID.METADATA.regexp):
            return False
        return NationalID.parse(id_number) is not None

    @staticmethod
    def parse(id_number: str) -> Optional[ParseResult]:
        """parse the result"""
        match_obj = NationalID.METADATA.regexp.match(id_number)
        return NationalID.build_parse_result(match_obj)

    @staticmethod
    def build_parse_result(match_obj: re.Match[str]) -> Optional[ParseResult]:
        if not match_obj:
            return None
        yy = int(match_obj.group('yy'))
        mm = int(match_obj.group('mm'))
        dd = int(match_obj.group('dd'))
        gender = int(match_obj.group('gender'))
        sn = match_obj.group('sn')
        yyyy_base = NationalID.DOB_BASE_MAP[gender]
        try:
            return {
                'yyyymmdd': date(yyyy_base + yy, mm, dd),
                'gender': Gender.MALE if gender % 2 == 1 else Gender.FEMALE,
                'citizenship': NationalID.CITIZENSHIP_MAP[gender],
                'sn': sn
            }
        except ValueError:
            return None


"""
The ARC is the same as NationalID
"""
ARC = NationalID


class OldNationalID(NationalID):
    """
    KOR National ID number format. The ARC is the same as NationalID.
    # https://en.wikipedia.org/wiki/Resident_registration_number
    # https://centers.ibs.re.kr/html/living_en/overview/arc.html
    """
    METADATA = SimpleNamespace(**{
        'iso3166_alpha2': 'KR',
        'min_length': 13,
        'max_length': 13,
        'parsable': True,
        'checksum': True,
        'regexp': re.compile(r'^(?P<yy>\d{2})(?P<mm>\d{2})(?P<dd>\d{2})-'
                             r'(?P<gender>\d)'
                             r'(?P<location>\d{4})'
                             r'(?P<sn>\d)'
                             r'(?P<checksum>\d)$')
    })

    MAGIC_MULTIPLIER = [2, 3, 4, 5, 6, 7, 8, 9, 2, 3, 4, 5]
    """multiplier for the checksum"""

    @staticmethod
    def validate(id_number: str) -> bool:
        """
        Validate the old KOR id number
        """
        if not validate_regexp(id_number, NationalID.METADATA.regexp):
            return False
        return OldNationalID.parse(id_number) is not None

    @staticmethod
    def parse(id_number: str) -> Optional[OldIDParseResult]:
        """prase the result"""
        match_obj = re.match(OldNationalID.METADATA.regexp, id_number)
        new_result = NationalID.parse(id_number)
        if not new_result:
            return None
        if not OldNationalID.checksum(id_number):
            return None
        return {
            **new_result,
            'sn': match_obj.group('sn'),
            'location': match_obj.group('location'),
            'checksum': int(match_obj.group('checksum'))
        }

    @staticmethod
    def checksum(id_number) -> bool:
        """multiply the magic number and find the modulus"""
        if not validate_regexp(id_number, OldNationalID.METADATA.regexp):
            return False
        normalized = normalize(id_number)
        # it uses modulus 11 algorithm with magic numbers
        numbers = [int(char) for char in normalized]
        modulus = modulus_overflow_mod10(weighted_modulus_digit(numbers[:-1], OldNationalID.MAGIC_MULTIPLIER, 11))
        return modulus == numbers[-1]
