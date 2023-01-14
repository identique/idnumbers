import re
from types import SimpleNamespace
from typing import Optional, TypedDict
from datetime import date

from .util import validate_regexp
from .constant import Gender


class ParseResult(TypedDict):
    """parse result of National ID"""
    gender: Gender
    """gender, possible value: male, female"""
    yyyymmdd: date
    """dob"""
    checksum: str
    """checksum, 2 digits"""


class NationalID:
    """
    Norway National ID number
    https://en.wikipedia.org/wiki/National_identification_number#Norway
    https://en.wikipedia.org/wiki/National_identity_number_(Norway)
    """
    METADATA = SimpleNamespace(**{
        'iso3166_alpha2': 'NO',
        # length without insignificant chars
        'min_length': 11,
        'max_length': 11,
        'parsable': True,
        'checksum': True,
        'regexp': re.compile(r'^(?P<dd>\d{2})'
                             r'(?P<mm>\d{2})'
                             r'(?P<yy>\d{2})'
                             r'(?P<individual_number>\d{3})'
                             r'(?P<checksum>\d{2})$')
    })

    @staticmethod
    def validate(id_number: str) -> bool:
        """
        Validate the NOR id number
        """
        if not validate_regexp(id_number, NationalID.METADATA.regexp):
            return False
        if not NationalID.parse(id_number):
            return False
        return NationalID.checksum(id_number)

    @staticmethod
    def parse(id_number: str) -> Optional[ParseResult]:
        """parse the result"""
        match_obj = NationalID.METADATA.regexp.match(id_number)
        if not match_obj:
            return None

        individual_code = match_obj.group('individual_number')
        yy = match_obj.group('yy')
        mm = match_obj.group('mm')
        dd = match_obj.group('dd')

        birth_century = '20'
        individual_num = int(individual_code)
        if 0 <= individual_num < 500:
            birth_century = 19
        elif 500 <= individual_num < 750 and int(yy) >= 54:
            birth_century = 18
        elif 900 <= individual_num < 1000 and int(yy) >= 40:
            birth_century = 19

        return {
            "gender": Gender.FEMALE if int(individual_code[2]) % 2 == 0 else Gender.MALE,
            'yyyymmdd': date(int(f'{birth_century}{yy}'), int(mm), int(dd)),
            "checksum": match_obj.group('checksum')
        }

    FIRST_MAGIC_MULTIPLIER = [3, 7, 6, 1, 8, 9, 4, 5, 2, 1]
    SECOND_MAGIC_MULTIPLIER = [5, 4, 3, 2, 7, 6, 5, 4, 3, 2, 1]

    @staticmethod
    def checksum(id_number: str) -> bool:
        """algorithm: https://en.wikipedia.org/wiki/National_identity_number_(Norway)#Check_digits"""
        if not validate_regexp(id_number, NationalID.METADATA.regexp):
            return False
        number_list = [int(char) for char in id_number]
        # Digit 10th
        first_total = sum([value * number_list[idx] for (idx, value) in enumerate(NationalID.FIRST_MAGIC_MULTIPLIER)])
        # Digit 11th
        second_total = sum([value * number_list[idx] for (idx, value) in enumerate(NationalID.SECOND_MAGIC_MULTIPLIER)])
        return first_total % 11 == 0 and second_total % 11 == 0
