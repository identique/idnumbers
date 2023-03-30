import re
from types import SimpleNamespace
from typing import Optional, TypedDict
from ..util import CHECK_DIGIT, validate_regexp
from .util import EntityType, EntityDivision, checksum


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
                             r'(?P<checksum>\d)$'),
        'alias_of': None,
        'names': ['Business Identification Number',
                  'Бизнес-идентификационный номер'],
        'links': ['https://korgan-zan.kz/en/obtaining-iin-and-bin-in-kazakhstan/'],
        'deprecated': False
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
