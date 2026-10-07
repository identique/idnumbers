import re
from datetime import date
from types import SimpleNamespace
from typing import Optional, TypedDict, Tuple, cast
from ..constant import Citizenship, Gender
from ..util import CHECK_DIGIT, weighted_modulus_digit, validate_regexp, match_regexp


class ParseResult(TypedDict):
    """parse result of CNP"""
    yyyymmdd: date
    """dob"""
    location: str
    """registration location"""
    gender: Gender
    """gender: male, female"""
    citizenship: Citizenship
    """citizenship or resident"""
    sn: str
    """serial number"""
    checksum: CHECK_DIGIT
    """checksum digit"""


class PersonalNumericalCode:
    """
    Personal Numerical Code (Cod Numeric Personal, CNP)
    https://en.wikipedia.org/wiki/National_identification_number#Romania
    https://en.wikipedia.org/wiki/Romanian_identity_card
    https://github.com/vimishor/cnp-spec/blob/master/spec.md
    """
    METADATA = SimpleNamespace(**{
        'iso3166_alpha2': 'RO',
        'min_length': 13,
        'max_length': 13,
        'parsable': True,
        'checksum': True,
        'regexp': re.compile(r'^(?P<gender_century>\d)'
                             r'(?P<yy>\d{2})(?P<mm>\d{2})(?P<dd>\d{2})'
                             r'(?P<location>\d{2})'
                             r'(?P<sn>\d{3})'
                             r'(?P<checksum>\d)$'),
        'alias_of': None,
        'names': ['Personal Numerical Code',
                  'Cod Numeric Personal',
                  'CNP',
                  'Carte de identitate'],
        'links': ['https://en.wikipedia.org/wiki/National_identification_number#Romania',
                  'https://en.wikipedia.org/wiki/Romanian_identity_card',
                  'https://github.com/vimishor/cnp-spec/blob/master/spec.md'],
        'deprecated': False
    })

    MAGIC_MULTIPLIER = [2, 7, 9, 1, 4, 6, 3, 5, 8, 2, 7, 9]
    """multiplier for checksum"""

    YEAR_BASE_MAP = [1900, 1900, 1800, 1800, 2000, 2000]
    """
    century base of the first digit (sex and century) 1..6, so it is indexed by that digit minus 1:
    1, 2 = 1900-1999; 3, 4 = 1800-1899; 5, 6 = 2000-2099. Residents (7, 8) are resolved from yy instead.
    https://github.com/vimishor/cnp-spec/blob/master/spec.md
    """

    @staticmethod
    def validate(id_number: str) -> bool:
        """
        Validate the personal numerical code
        """
        if not validate_regexp(id_number, PersonalNumericalCode.METADATA.regexp):
            return False
        return PersonalNumericalCode.parse(id_number) is not None

    @staticmethod
    def parse(id_number: str) -> Optional[ParseResult]:
        """parse the value"""
        match_obj = match_regexp(id_number, PersonalNumericalCode.METADATA.regexp)
        if not match_obj:
            return None
        checksum = PersonalNumericalCode.checksum(id_number)
        if not checksum:
            return None
        location = match_obj.group('location')
        if not (1 <= int(location) <= 52 or location == '99'):
            return None
        gender_century = int(match_obj.group('gender_century'))
        yy = int(match_obj.group('yy'))
        data = PersonalNumericalCode.get_gender_citizenship_year_base(gender_century, yy)
        if not data:
            return None
        gender, citizenship, year_base = data
        mm = int(match_obj.group('mm'))
        dd = int(match_obj.group('dd'))
        sn = match_obj.group('sn')
        try:
            return {
                'yyyymmdd': date(year_base + yy, mm, dd),
                'location': location,
                'gender': gender,
                'citizenship': citizenship,
                'sn': sn,
                'checksum': cast(CHECK_DIGIT, int(match_obj.group('checksum')))
            }
        except ValueError:
            return None

    @staticmethod
    def get_gender_citizenship_year_base(gender_century: int, yy: int) -> Optional[Tuple[Gender, Citizenship, int]]:
        if gender_century > 8 or gender_century < 1:
            return None
        gender = Gender.MALE if gender_century % 2 == 1 else Gender.FEMALE
        citizenship = Citizenship.CITIZEN if gender_century < 7 else Citizenship.RESIDENT
        if gender_century < 7:
            year_base = PersonalNumericalCode.YEAR_BASE_MAP[gender_century - 1]
        else:
            year_base = 2000 if yy < 50 else 1900
        return gender, citizenship, year_base

    @staticmethod
    def checksum(id_number: str) -> bool:
        """
        algorithm:
        https://en.wikipedia.org/wiki/National_identification_number#Romania
        """
        if not validate_regexp(id_number, PersonalNumericalCode.METADATA.regexp):
            return False
        numbers = [int(char) for char in id_number]
        modulus = weighted_modulus_digit(numbers[:-1], PersonalNumericalCode.MAGIC_MULTIPLIER, 11, True)
        if modulus == 10:
            modulus = 1
        return modulus == numbers[-1]
