import re
from types import SimpleNamespace
from typing import Literal, Optional
from ..util import weighted_modulus_digit, modulus_overflow_mod10, validate_regexp
from .resident_registration import ResidentRegistration, ParseResult


def normalize(id_number):
    """strip out useless characters/whitespaces"""
    return re.sub(r'-', '', id_number)


class OldIDParseResult(ParseResult):
    """Old format contains more information"""
    location: str
    """registration location"""
    checksum: Literal[0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    """check digits"""


class OldResidentRegistration(ResidentRegistration):
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
                             r'(?P<checksum>\d)$'),
        'alias_of': None,
        'names': ['Resident Registration Number',
                  '주민등록번호',
                  'RRN',
                  '住民登錄番號',
                  'Jumin Deungnok Beonho'],
        'links': ['https://en.wikipedia.org/wiki/Resident_registration_number',
                  'https://centers.ibs.re.kr/html/living_en/overview/arc.html'],
        'deprecated': True
    })

    MAGIC_MULTIPLIER = [2, 3, 4, 5, 6, 7, 8, 9, 2, 3, 4, 5]
    """multiplier for the checksum"""

    @staticmethod
    def validate(id_number: str) -> bool:
        """
        Validate the old KOR id number
        """
        if not validate_regexp(id_number, OldResidentRegistration.METADATA.regexp):
            return False
        return OldResidentRegistration.parse(id_number) is not None

    @staticmethod
    def parse(id_number: str) -> Optional[OldIDParseResult]:
        """prase the result"""
        match_obj = re.match(OldResidentRegistration.METADATA.regexp, id_number)
        new_result = ResidentRegistration.parse(id_number)
        if not new_result:
            return None
        if not OldResidentRegistration.checksum(id_number):
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
        if not validate_regexp(id_number, OldResidentRegistration.METADATA.regexp):
            return False
        normalized = normalize(id_number)
        # it uses modulus 11 algorithm with magic numbers
        numbers = [int(char) for char in normalized]
        modulus = modulus_overflow_mod10(
            weighted_modulus_digit(numbers[:-1], OldResidentRegistration.MAGIC_MULTIPLIER, 11))
        return modulus == numbers[-1]
