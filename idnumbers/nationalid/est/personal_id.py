import re
from ..util import birth_date as _calendar_date
from datetime import date
from ..metadata import IdMetadata
from typing import Optional, Tuple, TypedDict, cast
from ..constant import Gender
from ..util import CHECK_DIGIT, validate_regexp, weighted_modulus_digit, match_regexp


class ParseResult(TypedDict):
    """The parse result of Resident ID"""
    yyyymmdd: date
    """birthday"""
    sn: str
    """serial number"""
    gender: Gender
    """gender, possible value: male, female"""
    checksum: CHECK_DIGIT
    """checksum digit, numbers or 'X'"""


class PersonalID:
    """
    Estonia Personal ID number format, isikukood
    https://en.wikipedia.org/wiki/National_identification_number#Estonia
    https://et.wikipedia.org/wiki/Isikukood
    """
    METADATA = IdMetadata(**{
        'iso3166_alpha2': 'EE',
        'min_length': 11,
        'max_length': 11,
        'parsable': True,
        'checksum': True,
        'regexp': re.compile(r'^(?P<gender_century>\d)'
                             r'(?P<yy>\d{2})(?P<mm>\d{2})(?P<dd>\d{2})'
                             r'(?P<sn>\d{3})'
                             r'(?P<checksum>\d)$'),
        'alias_of': None,
        'names': ['Personal ID Number',
                  'isikukood'],
        'links': ['https://en.wikipedia.org/wiki/National_identification_number#Estonia',
                  'https://et.wikipedia.org/wiki/Isikukood'],
        'deprecated': False,
        'country_name': 'Estonia',
        'id_type': 'Personal ID Number',
        'official_name': 'isikukood',
        'display_format': 'GYYMMDDSSSC',
        'example': '37605030299',
        'checksum_algorithm': 'Weighted sum mod 11 in two passes (weights 1-9 and 1; then 3-9, 1, 2 and 3 when the '
                              'remainder is 10; a second 10 becomes 0)',
        'masks': ('###########',)
    })

    WEIGHTS1 = [1, 2, 3, 4, 5, 6, 7, 8, 9, 1]
    WEIGHTS2 = [3, 4, 5, 6, 7, 8, 9, 1, 2, 3]

    @staticmethod
    def validate(id_number: str) -> bool:
        """
        Validate the personal id number
        """
        if not isinstance(id_number, str) or not id_number:
            return False
        return PersonalID.parse(id_number) is not None

    @staticmethod
    def parse(id_number: str) -> Optional[ParseResult]:
        """parse the data"""
        match_obj = match_regexp(id_number, PersonalID.METADATA.regexp)
        if not match_obj:
            return None
        checksum_str = match_obj.group('checksum')
        checksum = PersonalID.checksum(id_number)
        if checksum is None or str(checksum) != checksum_str:
            return None
        gender_year_base = PersonalID.get_gender_year_base(int(match_obj.group('gender_century')))
        if gender_year_base is None:
            return None
        gender, year_base = gender_year_base
        try:
            sn = match_obj.group('sn')
            calendar_date = _calendar_date(int(match_obj.group('yy')) + year_base,
                                 int(match_obj.group('mm')),
                                 int(match_obj.group('dd')))
            if calendar_date is None:
                return None
            return {
                'yyyymmdd': calendar_date,
                'sn': sn,
                'gender': gender,
                'checksum': checksum
            }
        except ValueError:
            return None

    @staticmethod
    def get_gender_year_base(gender_century: int) -> Optional[Tuple[Gender, int]]:
        gender = Gender.MALE if gender_century % 2 == 1 else Gender.FEMALE
        if 0 < gender_century <= 2:
            year_base = 1800
        elif 2 < gender_century <= 4:
            year_base = 1900
        elif 4 < gender_century <= 6:
            year_base = 2000
        elif 6 < gender_century <= 8:
            year_base = 2100
        else:
            return None
        return gender, year_base

    @staticmethod
    def checksum(id_number: str) -> Optional[CHECK_DIGIT]:
        """algorithm: https://et.wikipedia.org/wiki/Isikukood#Kontrollnumber"""
        if not validate_regexp(id_number, PersonalID.METADATA.regexp):
            return None
        numbers = [int(char) for char in id_number]
        checksum = weighted_modulus_digit(numbers[0:-1], PersonalID.WEIGHTS1, 11, True)
        if checksum == 10:
            # use 2 phase weights when it is 10
            checksum = weighted_modulus_digit(numbers[0:-1], PersonalID.WEIGHTS2, 11, True)
            if checksum == 10:
                # reset to 0 if it is 10 at the 2nd phase
                checksum = 0
        return cast(CHECK_DIGIT, checksum)
