import re
from ..util import birth_date as _calendar_date
from datetime import date
from ..metadata import IdMetadata
from typing import Optional, TypedDict
from ..util import validate_regexp, match_regexp


class ParseResult(TypedDict):
    """The parse result of the Danish personal identity number, CPR"""
    yyyymmdd: date
    """Birthday"""
    sn: str
    """The serial number born at the same date"""


def _century_base(yy: int, first_sn_digit: int) -> int:
    """
    The first year of the century of the birth date, from the year digits and the first digit of the serial number.
    https://cpr.dk/media/12066/personnummeret-i-cpr.pdf
    """
    if first_sn_digit <= 3:
        return 1900
    if first_sn_digit in (4, 9):
        return 2000 if yy <= 36 else 1900
    return 2000 if yy <= 57 else 1800


class PersonalIdentityNumber:
    """
    Denmark personal identity number, CPR, Det Centrale Personregister
    https://en.wikipedia.org/wiki/National_identification_number#Denmark
    CPR numbers issued after 1 October 2007 can have a different format meaning that the last digit is not a check digit
    and can therefore not be verified on the TIN on Europa web portal.

    The century of the birth date comes from the year digits (positions 5-6) together with the first digit of the
    serial number (position 7), see the table "Personnummerets opbygning" in
    https://cpr.dk/media/12066/personnummeret-i-cpr.pdf and
    https://cpr.dk/cpr-systemet/opbygning-af-cpr-nummeret .
    A birth date in the future is rejected.
    """
    METADATA = IdMetadata(**{
        'iso3166_alpha2': 'DK',
        'min_length': 10,
        'max_length': 10,
        'parsable': True,
        'checksum': False,
        'regexp': re.compile(r'^(?P<dd>\d{2})(?P<mm>\d{2})(?P<yy>\d{2})-?'
                             r'(?P<sn>\d{4})$'),
        'alias_of': None,
        'names': ['personal identity number',
                  'CPR',
                  'Det Centrale Personregister'],
        'links': ['https://en.wikipedia.org/wiki/National_identification_number#Denmark',
                  'https://cpr.dk/media/12066/personnummeret-i-cpr.pdf',
                  'https://cpr.dk/cpr-systemet/opbygning-af-cpr-nummeret'],
        'deprecated': False,
        'country_name': 'Denmark',
        'id_type': 'Personal Identity Number',
        'official_name': 'CPR-nummer',
        'display_format': 'DDMMYY-SSSS',
        'example': '010100-1234',
        'checksum_algorithm': None,
        'masks': ('######-####',)
    })

    @staticmethod
    def validate(id_number: str) -> bool:
        """
        Validate the id number
        """
        if not validate_regexp(id_number, PersonalIdentityNumber.METADATA.regexp):
            return False
        return PersonalIdentityNumber.parse(id_number) is not None

    @staticmethod
    def parse(id_number: str) -> Optional[ParseResult]:
        """ parse the CPR id"""
        match_obj = match_regexp(id_number, PersonalIdentityNumber.METADATA.regexp)
        if not match_obj:
            return None
        yy = int(match_obj.group('yy'))
        mm = int(match_obj.group('mm'))
        dd = int(match_obj.group('dd'))
        sn = match_obj.group('sn')
        try:
            birth_date = _calendar_date(_century_base(yy, int(sn[0])) + yy, mm, dd)
            if birth_date is None:
                return None
        except ValueError:
            return None
        if birth_date > date.today():
            return None
        return {
            'yyyymmdd': birth_date,
            'sn': sn
        }
