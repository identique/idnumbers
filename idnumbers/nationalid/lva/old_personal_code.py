import re
from datetime import date
from typing import Optional, Union, TypedDict
from types import SimpleNamespace

from ..util import CHECK_DIGIT, validate_regexp
from .personal_code import PersonalCode


class OldParseResult(TypedDict):
    """parse result for the national id"""
    yyyymmdd: date
    """birthday"""
    sn: str
    """serial number"""
    checksum: CHECK_DIGIT
    """check digits"""


class OldPersonalCode:
    """
    Old Latvia personal code format, personas kods
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
                             r'(?P<checksum>\d)$'),
        'alias_of': None,
        'names': ['Personal Code',
                  'personas kods'],
        'links': ['https://en.wikipedia.org/wiki/National_identification_number#Latvia',
                  'https://www.oecd.org/tax/automatic-exchange/crs-implementation-and-assistance/'
                  'tax-identification-numbers/Latvia-TIN.pdf'],
        'deprecated': True
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
        if id_number[-1] != str(checksum):
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
    def checksum(id_number: str) -> Optional[CHECK_DIGIT]:
        """Use new personal code to calculate the checksum"""
        return PersonalCode.checksum(id_number)
