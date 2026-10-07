import re
from types import SimpleNamespace
from typing import Literal, Optional, TypedDict, cast
from ..constant import Gender
from ..util import CHECK_DIGIT, weighted_modulus_digit, validate_regexp, match_regexp


LOCATION_CODE = Literal['A', 'B', 'C', 'D', 'E', 'F', 'G',
                        'H', 'I', 'J', 'K', 'L', 'M', 'N',
                        'O', 'P', 'Q', 'R', 'S', 'T', 'U',
                        'V', 'W', 'X', 'Y', 'Z']
"""letter of the location code"""


class ParseResult(TypedDict):
    location: LOCATION_CODE
    """location code"""
    gender: Gender
    """gender: male or female"""
    sn: str
    """serial number"""
    checksum: CHECK_DIGIT


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
                             r'(?P<checksum>\d)$'),
        'alias_of': None,
        'names': ['National ID Number',
                  '國民身分證統一編號',
                  '身分證字號'],
        'links': ['https://en.wikipedia.org/wiki/National_identification_number#Taiwan',
                  'https://zh.wikipedia.org/wiki/'
                  '%E4%B8%AD%E8%8F%AF%E6%B0%91%E5%9C%8B%E5%9C%8B%E6%B0%91%E8%BA%AB%E5%88%86%E8%AD%89'],
        'deprecated': False
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
        match_obj = match_regexp(id_number, NationalID.METADATA.regexp)
        if not match_obj:
            return None
        checksum = NationalID.checksum(id_number)
        if str(checksum) != id_number[-1]:
            return None
        location = match_obj.group('location')
        gender = match_obj.group('gender')
        sn = match_obj.group('sn')
        return {
            'location': cast(LOCATION_CODE, location),
            'gender': Gender.MALE if gender == '1' else Gender.FEMALE,
            'sn': sn,
            'checksum': cast(CHECK_DIGIT, int(match_obj.group('checksum')))
        }

    @staticmethod
    def checksum(id_number: str) -> Optional[CHECK_DIGIT]:
        """
        Calculate the TWN national id number check digit.
        Returns None when the input is not a well-formed id number.

        The check digit (0-9) is (10 - S % 10) % 10, where S is the sum of the two digits of the location code
        followed by the next eight digits (gender and serial number), weighted 1, 9, 8, 7, 6, 5, 4, 3, 2, 1.
        A weighted sum that is a multiple of 10 therefore gives 0, not 10.
        https://zh.wikipedia.org/wiki/%E4%B8%AD%E8%8F%AF%E6%B0%91%E5%9C%8B%E5%9C%8B%E6%B0%91%E8%BA%AB%E5%88%86%E8%AD%89#%E6%9C%89%E6%95%88%E7%A2%BC
        """
        if not validate_regexp(id_number, NationalID.METADATA.regexp):
            return None
        # it uses modulus 10 algorithm with magic numbers
        location = id_number[0]
        numbers = NationalID.LOCATION_NUM[ord(location) - 65] + [int(char) for char in id_number[1:]]
        # a weighted sum that is a multiple of 10 gives check digit 0, not 10
        return cast(CHECK_DIGIT, weighted_modulus_digit(numbers[:-1], NationalID.MAGIC_MULTIPLIER, 10) % 10)
