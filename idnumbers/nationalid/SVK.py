import re
from datetime import date
from typing import Optional, TypedDict
from types import SimpleNamespace

from .constant import Gender
from .util import CHECK_DIGIT, validate_regexp


class BirthNumberParseResult(TypedDict):
    yyyymmdd: date
    """birthday of this ID, there is no way to know the century of the birthday. So, yy < 50 is 20yy else 19yy."""
    gender: Gender
    """only male or female"""
    sn: str
    """serial number"""
    checksum: CHECK_DIGIT
    """checksum"""


class BirthNumber:
    """
    Slovakia Birth Number format, rodné číslo (RČ)
    https://en.wikipedia.org/wiki/National_identification_number#Slovakia
    """
    METADATA = SimpleNamespace(**{
        'iso3166_alpha2': 'SK',
        'min_length': 10,
        'max_length': 10,
        # length without insignificant chars
        'parsable': True,
        # has parse function
        'checksum': True,
        # has checksum function
        'regexp': re.compile(r'^(?P<yy>\d{2})'
                             r'(?P<mm>\d{2})'
                             r'(?P<dd>\d{2})/?'
                             r'(?P<sn>\d{3})'
                             r'(?P<checksum>\d)$')
        # regular expression to validate the id
    })

    @staticmethod
    def validate(id_number: str) -> bool:
        """
        Validate birth number
        """
        if not validate_regexp(id_number, BirthNumber.METADATA.regexp):
            return False
        return BirthNumber.parse(id_number) is not None

    @staticmethod
    def parse(id_number: str) -> Optional[BirthNumberParseResult]:
        """
        parse the id number
        """
        match_obj = BirthNumber.METADATA.regexp.match(id_number)
        if not match_obj:
            return None

        if not BirthNumber.checksum(id_number):
            return None

        yy = int(match_obj.group('yy'))
        mm_code = int(match_obj.group('mm'))
        dd = int(match_obj.group('dd'))
        mm = mm_code if mm_code < 50 else mm_code - 50
        """
        from https://en.wikipedia.org/wiki/National_identification_number#Czech_Republic_and_Slovakia
        In a law that took place in the year 2004, a failsafe system has been implemented, where in case
        all valid serial numbers get depleted for a day, the number 20 gets added to the value of XX.
        This means that XX can get up to 32 for males, and 82 for females.
        """
        mm = mm - 20 if mm > 20 else mm
        year_base = 2000 if yy < 50 else 1900
        try:
            return {
                'yyyymmdd': date(year_base + yy, mm, dd),
                'gender': Gender.MALE if mm_code < 50 else Gender.FEMALE,
                'sn': match_obj.group('sn'),
                'checksum': int(match_obj.group('checksum'))
            }
        except ValueError:
            return None

    @staticmethod
    def checksum(id_number: str) -> bool:
        """
        Calculate SVK BirthNumber checksum digit
        """
        if not validate_regexp(id_number, BirthNumber.METADATA.regexp):
            return False
        return int(BirthNumber.normalize(id_number)) % 11 == 0

    @staticmethod
    def normalize(id_number: str) -> str:
        """remove the / out"""
        return re.sub(r'/', '', id_number)


class CitizenIDNumber:
    """
    Slovakia Citizen Identification Card Number format, Číslo občianskeho preukazu (ČOP)
    https://en.wikipedia.org/wiki/National_identification_number#Slovakia
    https://en.wikipedia.org/wiki/Slovak_identity_card
    """
    METADATA = SimpleNamespace(**{
        'iso3166_alpha2': 'SK',
        'min_length': 8,
        'max_length': 8,
        # length without insignificant chars
        'parsable': False,
        # has parse function
        'checksum': False,
        # has checksum function
        'regexp': re.compile(r'^[A-Z]{2} ?\d{6}$')
        # regular expression to validate the id
    })

    @staticmethod
    def validate(id_number: str) -> bool:
        """
        Validate CitizenIDNumber
        """
        return validate_regexp(id_number, CitizenIDNumber.METADATA.regexp)


NationalID = BirthNumber
"""alias of BirthNumber"""
