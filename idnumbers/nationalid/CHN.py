import re
from datetime import date
from types import SimpleNamespace
from typing import Literal, Optional, TypedDict
from .constant import Gender
from .util import validate_regexp


def normalize(id_number: str) -> str:
    return id_number.upper() if id_number else None


class ParseResult(TypedDict):
    address_code: str
    yyyymmdd: date
    sn: int
    gender: Gender
    checksum: Literal[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 'X']


class ResidentIDNumber:
    """
    China Resident ID number format
    https://en.wikipedia.org/wiki/Resident_Identity_Card
    """
    METADATA = SimpleNamespace(**{
        'iso3166_alpha2': 'CN',
        'min_length': 18,
        'max_length': 18,
        'parsable': True,
        'checksum': True,
        'regexp': re.compile(r'^(?P<address_code>\d{6})'
                             r'(?P<yyyy>\d{4})'
                             r'(?P<mm>0[1-9]|1[12])'
                             r'(?P<dd>0[1-9]|[12][0-9]|3[01])'
                             r'(?P<sn>\d{3})'
                             r'(?P<checksum>(?:\d|X))$')
    })

    @staticmethod
    def validate(id_number: str) -> bool:
        """
        Validate the CHN id number
        """
        if not id_number:
            return False

        if not isinstance(id_number, str):
            id_number = repr(id_number)
        return ResidentIDNumber.parse(id_number) is not None

    @staticmethod
    def parse(id_number: str) -> Optional[ParseResult]:
        match_obj = ResidentIDNumber.METADATA.regexp.match(id_number)
        if not match_obj:
            return None
        address_code = match_obj.group('address_code')
        sn = match_obj.group('sn')
        checksum_str = match_obj.group('checksum')
        checksum = ResidentIDNumber.checksum(id_number)
        if checksum is None or str(checksum) != checksum_str:
            return None
        else:
            return {
                'address_code': address_code,
                'yyyymmdd': date(int(match_obj.group('yyyy')), int(match_obj.group('mm')), int(match_obj.group('dd'))),
                'sn': sn,
                'gender': Gender.FEMALE if int(sn) % 2 == 0 else Gender.MALE,
                'checksum': checksum
            }

    @staticmethod
    def checksum(id_number) -> Optional[Literal[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 'X']]:
        if not validate_regexp(id_number, ResidentIDNumber.METADATA.regexp):
            return None
        normalized = normalize(id_number)
        source_list = [int(char) for char in normalized[:-1]]
        # The magic number is calculated from 2^(18 - i) % 11 (the first number is 1).
        total = sum([value * (pow(2, 17 - index) % 11) for (index, value) in enumerate(source_list)])
        checksum = (12 - total % 11) % 11
        return 'X' if checksum == 10 else checksum
