import re
from datetime import date
from typing import Optional, Union, TypedDict
from types import SimpleNamespace

from .util import CHECK_DIGIT, validate_regexp


def normalize(id_number):
    """strip out useless characters/whitespaces"""
    return re.sub(r'-', '', id_number)


def is_new_personal_code(id_number: str) -> bool:
    """use the first 2 char to determine the new or old format"""
    try:
        return int(id_number[0:2]) > 31
    except ValueError:
        return False


class OldParseResult(TypedDict):
    """parse result for the national id"""
    yyyymmdd: date
    """birthday"""
    sn: str
    """serial number"""
    checksum: CHECK_DIGIT
    """check digits"""


class PersonalCode:
    """
    Latvia national ID number format, personas kods
    https://en.wikipedia.org/wiki/National_identification_number#Latvia
    https://www.oecd.org/tax/automatic-exchange/crs-implementation-and-assistance/tax-identification-numbers/Latvia-TIN.pdf
    """
    METADATA = SimpleNamespace(**{
        'iso3166_alpha2': 'LV',
        # length without insignificant chars
        'min_length': 11,
        'max_length': 11,
        # has parse function
        'parsable': False,
        # has checksum function
        'checksum': True,
        # regular expression to validate the id
        'regexp': re.compile(r'^(\d{6}-?\d{5}$)')
    })

    MULTIPLIER = [1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
    """multiplier for checksum"""

    @staticmethod
    def validate(id_number: str) -> bool:
        """
        Validate national id number
        """
        if not validate_regexp(id_number, PersonalCode.METADATA.regexp):
            return False
        return PersonalCode.checksum(id_number) == id_number[-1]

    @staticmethod
    def checksum(id_number: str) -> str:
        """Calculate national id checksum: (1101-sum) mod 11 and mod 10"""
        numbers = [int(i) for i in normalize(id_number)[:10]]
        weighted_value = sum([value * PersonalCode.MULTIPLIER[index] for (index, value) in enumerate(numbers)])
        return str((1101 - weighted_value) % 11 % 10)


class OldPersonalCode:
    """
    Old Latvia national ID number format, personas kods
    https://en.wikipedia.org/wiki/National_identification_number#Latvia
    https://www.oecd.org/tax/automatic-exchange/crs-implementation-and-assistance/tax-identification-numbers/Latvia-TIN.pdf
    """
    METADATA = SimpleNamespace(**{
        'iso3166_alpha2': 'LV',
        # length without insignificant chars
        'min_length': 11,
        'max_length': 11,
        # has parse function
        'parsable': True,
        # has checksum function
        'checksum': True,
        # regular expression to validate the id
        'regexp': re.compile(r'^(?P<dd>\d{2})(?P<mm>\d{2})(?P<yy>\d{2})-?'
                             r'(?P<century>\d)'
                             r'(?P<sn>\d{3})'
                             r'(?P<checksum>\d)$')
    })

    MULTIPLIER = [1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
    """multiplier for checksum"""

    @staticmethod
    def validate(id_number: str) -> bool:
        """
        Validate national id number
        """
        if not validate_regexp(id_number, OldPersonalCode.METADATA.regexp):
            return False
        return OldPersonalCode.parse(id_number) is not None

    @staticmethod
    def parse(id_number: str) -> Optional[OldParseResult]:
        """parse the result"""
        match_obj = OldPersonalCode.METADATA.regexp.match(id_number)
        if not match_obj:
            return None
        checksum = OldPersonalCode.checksum(id_number)
        if id_number[-1] != checksum:
            return None

        if match_obj.group('century') == '0':
            year_base = 1800
        elif match_obj.group('century') == '1':
            year_base = 1900
        elif match_obj.group('century') == '2':
            year_base = 2000
        else:
            return None

        yy = int(match_obj.group('yy'))
        mm = int(match_obj.group('mm'))
        dd = int(match_obj.group('dd'))
        sn = match_obj.group('sn')
        try:
            return {
                'yyyymmdd': date(yy + year_base, mm, dd),
                'sn': sn,
                'checksum': int(match_obj.group('checksum'))
            }
        except ValueError:
            # check of wrong date data
            return None

    @staticmethod
    def checksum(id_number: str) -> str:
        """Use new personal code to calculate the checksum"""
        return PersonalCode.checksum(id_number)


def get_validator(id_number: str) -> Union[type[PersonalCode], type[OldPersonalCode]]:
    """check the first 2 char to return the correct class"""

    try:
        return PersonalCode if int(id_number[0:2]) > 31 else OldPersonalCode
    except ValueError:
        return OldPersonalCode


NationalID = PersonalCode
"""alias of PersonalCode"""
