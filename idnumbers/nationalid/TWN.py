import re
from types import SimpleNamespace
from typing import Literal, Optional, TypedDict
from .util import weighted_modulus_digit, validate_regexp
from .constant import Gender


class ParseResult(TypedDict):
    location: Literal['A', 'B', 'C', 'D', 'E', 'F', 'G',
                      'H', 'I', 'J', 'K', 'L', 'M', 'N',
                      'O', 'P', 'Q', 'R', 'S', 'T', 'U',
                      'V', 'W', 'X', 'Y', 'Z']
    gender: Gender
    sn: str
    checksum: Literal[0, 1, 2, 3, 4, 5, 6, 7, 8, 9]


class NationalID:
    """
    TWN National ID number format
    https://en.wikipedia.org/wiki/National_identification_number#Taiwan
    https://zh.wikipedia.org/wiki/%E4%B8%AD%E8%8F%AF%E6%B0%91%E5%9C%8B%E5%9C%8B%E6%B0%91%E8%BA%AB%E5%88%86%E8%AD%89
    python version of http://www2.lssh.tp.edu.tw/~hlf/class-1/lang-c/id/index.htm
    """
    METADATA = SimpleNamespace(**{
        'iso3166_alpha2': 'TW',
        'min_length': 10,
        'max_length': 10,
        'parsable': True,
        'checksum': True,
        'regexp': re.compile(r'^(?P<location>[A-Z])'
                             r'(?P<gender>[12])'
                             r'(?P<sn>\d{7})'
                             r'(?P<checksum>\d)$')
    })

    LOCATION_NUM = [[1, 0], [1, 1], [1, 2], [1, 3], [1, 4], [1, 5], [1, 6],
                    [1, 7], [3, 4], [1, 8], [1, 9], [2, 0], [2, 1], [2, 2],
                    [3, 5], [2, 3], [2, 4], [2, 5], [2, 6], [2, 7], [2, 8],
                    [2, 9], [3, 2], [3, 0], [3, 1], [3, 3]]
    """A-Z to numbers by index"""

    MAGIC_MULTIPLIER = [1, 9, 8, 7, 6, 5, 4, 3, 2, 1]
    """multiplier for checksum"""

    @staticmethod
    def validate(id_number: str) -> bool:
        """
        Validate the TWN id number
        """
        if not validate_regexp(id_number, NationalID.METADATA.regexp):
            return False
        return NationalID.parse(id_number) is not None

    @staticmethod
    def parse(id_number: str) -> Optional[ParseResult]:
        """parse the value"""
        match_obj = NationalID.METADATA.regexp.match(id_number)
        if not match_obj:
            return None
        location = match_obj.group('location')
        gender = match_obj.group('gender')
        sn = match_obj.group('sn')
        checksum = NationalID.checksum(id_number)
        if not checksum:
            return None
        else:
            return {
                'location': location,
                'gender': Gender.MALE if gender == '1' else Gender.FEMALE,
                'sn': sn,
                'checksum': int(match_obj.group('checksum'))
            }

    @staticmethod
    def checksum(id_number) -> bool:
        """
        algorithm:
        https://zh.wikipedia.org/wiki/%E4%B8%AD%E8%8F%AF%E6%B0%91%E5%9C%8B%E5%9C%8B%E6%B0%91%E8%BA%AB%E5%88%86%E8%AD%89#%E6%9C%89%E6%95%88%E7%A2%BC
        """
        if not validate_regexp(id_number, NationalID.METADATA.regexp):
            return False
        # it uses modulus 10 algorithm with magic numbers
        location = id_number[0]
        numbers = NationalID.LOCATION_NUM[ord(location) - 65] + [int(char) for char in id_number[1:]]
        modulus = weighted_modulus_digit(numbers[:-1], NationalID.MAGIC_MULTIPLIER, 10)
        return modulus == numbers[-1]
