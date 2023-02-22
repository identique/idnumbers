import re
from datetime import date
from types import SimpleNamespace
from typing import Optional, TypedDict, Tuple
from .util import CHECK_DIGIT, weighted_modulus_digit, validate_regexp
from .constant import Citizenship, Gender


def normalize(id_number):
    """strip out useless characters/whitespaces"""
    return re.sub(r'[ -]', '', id_number)


class ParseResult(TypedDict):
    """parse result for the national id"""
    yyyymmdd: date
    """birthday"""
    gender: Gender
    """gender, possible value: male, female"""
    citizenship: Citizenship
    """possible value: citizen meaning born from hungary, foreign: meaning naturalized citizen or resident"""
    sn: str
    """serial number"""
    checksum: CHECK_DIGIT
    """check digits"""


class PersonalID:
    """
    Hungary Personal ID number format
    https://en.wikipedia.org/wiki/National_identification_number#Hungary
    """
    METADATA = SimpleNamespace(**{
        'iso3166_alpha2': 'HU',
        'min_length': 11,
        'max_length': 11,
        'parsable': True,
        'checksum': True,
        'regexp': re.compile(r'^(?P<gender>\d)[ -]?'
                             r'(?P<yy>\d{2})(?P<mm>\d{2})(?P<dd>\d{2})[ -]?'
                             r'(?P<sn>\d{3})'
                             r'(?P<checksum>\d)$')
    })

    MAGIC_MULTIPLIER = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    """multiplier for the checksum"""

    @staticmethod
    def validate(id_number: str) -> bool:
        """
        Validate the personal id number
        """
        if not validate_regexp(id_number, PersonalID.METADATA.regexp):
            return False
        return PersonalID.parse(id_number) is not None

    @staticmethod
    def parse(id_number: str) -> Optional[ParseResult]:
        """parse the result"""
        match_obj = PersonalID.METADATA.regexp.match(id_number)
        if not match_obj:
            return None
        checksum = PersonalID.checksum(id_number)
        if not checksum:
            return None
        gender_citizenship_year_base = PersonalID.get_gender_citizenship_year_base(int(match_obj.group('gender')))
        if not gender_citizenship_year_base:
            return None
        gender, citizenship, year_base = gender_citizenship_year_base
        yy = int(match_obj.group('yy'))
        mm = int(match_obj.group('mm'))
        dd = int(match_obj.group('dd'))
        sn = match_obj.group('sn')
        try:
            return {
                'yyyymmdd': date(yy + year_base, mm, dd),
                'gender': gender,
                'citizenship': citizenship,
                'sn': sn,
                'checksum': int(match_obj.group('checksum'))
            }
        except ValueError:
            return None

    @staticmethod
    def checksum(id_number) -> bool:
        """
        It's hard to find it. The algorithm is the 11-modulus on a weighted sum.
        algorithm: https://github.com/loonkwil/hungarian-validator-bundle/blob/master/Validator/PersonalIdValidator.php
        """
        if not validate_regexp(id_number, PersonalID.METADATA.regexp):
            return False
        # it uses modulus 11 algorithm with magic numbers
        numbers = [int(char) for char in normalize(id_number)]
        modulus = weighted_modulus_digit(numbers[:-1], PersonalID.MAGIC_MULTIPLIER, 11, True)
        # According to an official doc in hungary language, gov will use another random number to
        # skip the modulus 10.
        return modulus == numbers[-1] if modulus < 10 else False

    @staticmethod
    def get_gender_citizenship_year_base(gender_citizenship: int) -> Optional[Tuple[Gender, Citizenship, int]]:
        gender = Gender.MALE if gender_citizenship % 2 == 1 else Gender.FEMALE
        citizenship = Citizenship.CITIZEN if gender_citizenship < 5 else Citizenship.FOREIGN
        if 0 < gender_citizenship <= 2:
            year_base = 1900
        elif 2 < gender_citizenship <= 4:
            year_base = 2000
        elif 4 < gender_citizenship <= 6:
            year_base = 1900
        elif 6 < gender_citizenship <= 8:
            year_base = 1800
        else:
            return None
        return gender, citizenship, year_base


NationalID = PersonalID
"""alias of PersonalID"""
