import re
from datetime import date
from ..metadata import IdMetadata
from typing import Literal, Optional, TypedDict, cast
from ..constant import Gender
from ..util import match_regexp


CHECKSUM_LETTER = Literal['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K',
                          'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'Y', 'U',
                          'V', 'W']  # cannot use CHECK_ALPHA because it ends with W
"""check letter of the id number"""


class ParseResult(TypedDict):
    """Parse result of id number"""
    yyyymmdd: date
    """year of birth"""
    sn: str
    """serial number"""
    gender: Gender
    """gender: male or female"""
    checksum: CHECKSUM_LETTER
    """check digits"""


class IdentityNumber:
    """
    Albania Identity Number, Numri i Identitetit (NID),  Numri i Identitetit të Shtetasit (NISH), NIPT

    The individual NID encodes the year, month (including gender) and day of birth:
    https://www.oecd.org/content/dam/oecd/en/topics/policy-issue-focus/aeoi/albania-tin.pdf (section II).
    Validation checks format and calendar dates and rejects future births; it does not verify the check letter
    algorithm or whether a number was issued. The existing historical year mapping is retained pending confirmation.
    """
    METADATA = IdMetadata(**{
        'iso3166_alpha2': 'AL',
        'min_length': 10,
        'max_length': 10,
        'parsable': True,
        'checksum': False,  # There is a checksum algorithm. But we cannot find it.
        'regexp': re.compile(r'^(?P<yy>[0-9A-T]\d)(?P<mm>\d{2})(?P<dd>\d{2})'
                             r'(?P<sn>\d{3})[ -]?'
                             r'(?P<checksum>[A-W])$'),
        'alias_of': None,
        'names': ['Albania Identity Number',
                  'Numri i Identitetit',
                  'NID',
                  'Numri i Identitetit të Shtetasit',
                  'NISH',
                  'NIPT'],
        'links': ['https://en.wikipedia.org/wiki/National_identification_number#Albania',
                  'https://www.oecd.org/content/dam/oecd/en/topics/policy-issue-focus/aeoi/albania-tin.pdf'],
        'deprecated': False,
        'country_name': 'Albania',
        'id_type': 'Identity Number',
        'official_name': 'Numri i Identitetit',
        'display_format': 'YYMMDDSSSC',
        'example': 'J50101001A',
        'checksum_algorithm': None,
        'masks': ('X########L',)
    })

    BASE_YEAR_MAP = '0123456789ABCDEFGHIJKLMNOPQRST'

    @staticmethod
    def validate(id_number: str) -> bool:
        """
        Validate format and a non-future calendar birth date, not checksum or issuance.
        """
        if not isinstance(id_number, str) or not id_number:
            return False
        return IdentityNumber.parse(id_number) is not None

    @staticmethod
    def parse(id_number: str) -> Optional[ParseResult]:
        """Parse the result, or return None for malformed input or a future birth date."""
        match_obj = match_regexp(id_number, IdentityNumber.METADATA.regexp)
        if not match_obj:
            return None
        yyyy = IdentityNumber.get_year(match_obj.group('yy'))
        mm = int(match_obj.group('mm'))
        dd = int(match_obj.group('dd'))
        try:
            birth_date = date(yyyy, mm if mm < 50 else mm - 50, dd)
            if birth_date > date.today():
                return None
            return {
                'yyyymmdd': birth_date,
                'gender': Gender.MALE if mm < 50 else Gender.FEMALE,
                'sn': match_obj.group('sn'),
                'checksum': cast(CHECKSUM_LETTER, match_obj.group('checksum'))
            }
        except ValueError:
            return None

    @staticmethod
    def get_year(yy: str) -> int:
        year_base = 1800 + IdentityNumber.BASE_YEAR_MAP.index(yy[0]) * 10
        return year_base + int(yy[1])
