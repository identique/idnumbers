import re
from datetime import date
from enum import Enum
from types import SimpleNamespace
from typing import Optional, Tuple, TypedDict
from .constant import Gender
from .util import CHECK_DIGIT, validate_regexp, weighted_modulus_digit


class EntityType(Enum):
    """Kazakhstan BIN entity type"""
    ResidentEntity = 'resident_entity'
    NonResidentEntity = 'non_resident_entity'
    IP = 'ip'


class EntityDivision(Enum):
    """Kazakhstan BIN entity division type"""
    HeadUnit = 'head_unit'
    Branch = 'branch'
    Representative = 'representative_office'
    Peasant = 'peasant'


class IINParseResult(TypedDict):
    """The parse result of IIN"""
    yyyymmdd: date
    """dob"""
    gender: Gender
    """gender: male and female"""
    sn: str
    """serial number"""
    checksum: CHECK_DIGIT
    """check digit"""


class BINParseResult(TypedDict):
    """The parse result of BIN"""
    yy: int
    """registration year (2 digits)"""
    mm: int
    """registration  month"""
    entity_type: EntityType
    """entity type"""
    entity_division: EntityDivision
    """type of this entity division"""
    sn: str
    """serial number"""
    checksum: CHECK_DIGIT
    """check digit"""


WEIGHTS1 = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
WEIGHTS2 = [3, 4, 5, 6, 7, 8, 9, 10, 11, 1, 2]


def checksum(id_number) -> Optional[CHECK_DIGIT]:
    """
    check the checksum
    https://www.oecd.org/tax/automatic-exchange/crs-implementation-and-assistance/tax-identification-numbers/Kazakhstan-TIN.pdf
    """
    numbers = [int(char) for char in id_number]
    modulus = weighted_modulus_digit(numbers[0:-1], WEIGHTS1, 11, True)
    if modulus == 10:
        modulus = weighted_modulus_digit(numbers[0:-1], WEIGHTS2, 11, True)
        # the second modulus will not be 10. If it is, it's wrong id number
    return modulus if modulus < 10 else None


class IndividualIDNumber:
    """
    Kazakhstan individual identification number, ЖСН, ZhSN, ИИН, IIN
    https://en.wikipedia.org/wiki/National_identification_number#Kazakhstan
    https://korgan-zan.kz/en/obtaining-iin-and-bin-in-kazakhstan/
    https://www.oecd.org/tax/automatic-exchange/crs-implementation-and-assistance/tax-identification-numbers/Kazakhstan-TIN.pdf
    """
    METADATA = SimpleNamespace(**{
        'iso3166_alpha2': 'KZ',
        'min_length': 12,
        'max_length': 12,
        'parsable': True,
        'checksum': True,
        'regexp': re.compile(r'^(?P<yy>\d{2})(?P<mm>\d{2})(?P<dd>\d{2})'
                             r'(?P<century>\d)'
                             r'(?P<sn>\d{4})'
                             r'(?P<checksum>\d)$')
    })

    @staticmethod
    def validate(id_number: str) -> bool:
        """validate"""
        if not validate_regexp(id_number, IndividualIDNumber.METADATA.regexp):
            return False
        return IndividualIDNumber.parse(id_number) is not None

    @staticmethod
    def parse(id_number: str) -> Optional[IINParseResult]:
        """parse the result"""
        match_obj = IndividualIDNumber.METADATA.regexp.match(id_number)
        if not match_obj:
            return None
        iin_checksum = IndividualIDNumber.checksum(id_number)
        if iin_checksum is None or iin_checksum != int(match_obj.group('checksum')):
            return None
        gender_year_base = IndividualIDNumber.get_gender_year_base(int(match_obj.group('century')))
        if not gender_year_base:
            return None
        gender, year_base = gender_year_base
        yy = int(match_obj.group('yy'))
        mm = int(match_obj.group('mm'))
        dd = int(match_obj.group('dd'))
        try:
            return {
                'yyyymmdd': date(yy + year_base, mm, dd),
                'gender': gender,
                'sn': match_obj.group('sn'),
                'checksum': int(match_obj.group('checksum')),
            }
        except ValueError:
            # catch the date error
            return None

    @staticmethod
    def checksum(id_number) -> Optional[CHECK_DIGIT]:
        if not validate_regexp(id_number, IndividualIDNumber.METADATA.regexp):
            return False
        return checksum(id_number)

    @staticmethod
    def get_gender_year_base(century: CHECK_DIGIT) -> Optional[Tuple[Gender, int]]:
        gender = Gender.MALE if century % 2 == 1 else Gender.FEMALE
        if 1 <= century < 3:
            year_base = 1800
        elif 3 <= century < 5:
            year_base = 1900
        elif 5 <= century < 7:
            year_base = 2000
        else:
            return None
        return gender, year_base


class BusinessIDNumber:
    """
    Kazakhstan Business identification number, Бизнес-идентификационный номер
    https://korgan-zan.kz/en/obtaining-iin-and-bin-in-kazakhstan/
    """
    METADATA = SimpleNamespace(**{
        'iso3166_alpha2': 'KZ',
        'min_length': 12,
        'max_length': 12,
        'parsable': True,
        'checksum': True,
        'regexp': re.compile(r'^(?P<yy>\d{2})(?P<mm>\d{2})'
                             r'(?P<type>[4-6])'
                             r'(?P<division>[0-3])'
                             r'(?P<sn>\d{5})'
                             r'(?P<checksum>\d)$')
    })

    ENTITY_TYPE_MAP = {
        '4': EntityType.ResidentEntity,
        '5': EntityType.ResidentEntity,
        '6': EntityType.ResidentEntity
    }

    DIVISION_TYPE_MAP = {
        '0': EntityDivision.HeadUnit,
        '1': EntityDivision.Branch,
        '2': EntityDivision.Representative,
        '3': EntityDivision.Peasant
    }

    @staticmethod
    def validate(id_number: str) -> bool:
        """validate"""
        if not validate_regexp(id_number, BusinessIDNumber.METADATA.regexp):
            return False
        return BusinessIDNumber.parse(id_number) is not None

    @staticmethod
    def parse(id_number: str) -> Optional[BINParseResult]:
        """parse the result"""
        match_obj = BusinessIDNumber.METADATA.regexp.match(id_number)
        if not match_obj:
            return None
        bin_checksum = BusinessIDNumber.checksum(id_number)
        if bin_checksum is None or bin_checksum != int(match_obj.group('checksum')):
            return None
        entity_type = match_obj.group('type')
        division = match_obj.group('division')
        if entity_type not in BusinessIDNumber.ENTITY_TYPE_MAP:
            return None
        if division not in BusinessIDNumber.DIVISION_TYPE_MAP:
            return None
        return {
            'yy': int(match_obj.group('yy')),
            'mm': int(match_obj.group('mm')),
            'entity_type': BusinessIDNumber.ENTITY_TYPE_MAP[entity_type],
            'entity_division': BusinessIDNumber.DIVISION_TYPE_MAP[division],
            'sn': match_obj.group('sn'),
            'checksum': int(match_obj.group('checksum')),
        }

    @staticmethod
    def checksum(id_number) -> Optional[CHECK_DIGIT]:
        if not validate_regexp(id_number, BusinessIDNumber.METADATA.regexp):
            return False
        return checksum(id_number)


NationalID = IndividualIDNumber
"""alias of IndividualIDNumber"""
