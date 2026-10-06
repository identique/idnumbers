import re
from datetime import date
from types import SimpleNamespace
from re import Match
from typing import Optional, TypedDict
from ..util import validate_regexp, match_regexp
from ..constant import Gender
from .util import calc_check_digits, normalize


class ParseResult(TypedDict):
    """The parse result of Belgium NationalID"""
    yyyymmdd: date
    """birthday"""
    gender: Gender
    """gender, possible value: male and female"""
    sn: str
    """serial number"""
    checksum: int
    """checksum digits, two digits"""


def _century(normalized: str) -> Optional[int]:
    """
    Infer the century of birth (1900 or 2000) from the check digits.

    The two-digit year is ambiguous, so the century can only be found by computing the check digits:
    for a person born from 2000 the digit 2 is put in front of the first nine digits (IT000).
    At most one of the two forms can match, because 2000000000 % 97 != 0.
    A 20xx birth year in the future is impossible, so the 2000 form is not accepted for it
    (python-stdnum does the same).

    :param normalized: the 11 digits, without separators
    :return: 1900, 2000, or None if neither form matches the check digits
    """
    base = int(normalized[:9])
    check = int(normalized[9:])
    if calc_check_digits(base) == check:
        return 1900
    if calc_check_digits(2000000000 + base) == check and 2000 + int(normalized[:2]) <= date.today().year:
        return 2000
    return None


def _birth_date(century: int, match_obj: Match[str]) -> Optional[date]:
    """Build the birth date, or return None if it is not a real calendar date."""
    try:
        return date(century + int(match_obj.group('yy')), int(match_obj.group('mm')), int(match_obj.group('dd')))
    except ValueError:
        return None


class NationalRegistrationNumber:
    """
    Belgium National register number format
    https://en.wikipedia.org/wiki/Belgian_identity_card

    """
    METADATA = SimpleNamespace(**{
        'iso3166_alpha2': 'BE',
        'min_length': 11,
        'max_length': 11,
        'parsable': True,
        'checksum': True,
        'regexp': re.compile(r'^(?P<yy>\d{2})\.?(?P<mm>\d{2})\.?(?P<dd>\d{2})-?'
                             r'(?P<sn>\d{3})\.?'
                             r'(?P<checksum>\d{2})$'),
        'alias_of': None,
        'names': ['National registration number',
                  'NN',
                  'Belgian identity card',
                  'Identiteitskaart',
                  'Carte d’identité',
                  'Personalausweis'],
        'links': ['https://en.wikipedia.org/wiki/Belgian_identity_card',
                  'https://www.checkdoc.be/CheckDoc/homepage.do'],
        'deprecated': False
    })

    @staticmethod
    def validate(id_number: str) -> bool:
        """validate the id"""
        match_obj = match_regexp(id_number, NationalRegistrationNumber.METADATA.regexp)
        if not match_obj:
            return False
        century = _century(normalize(id_number))
        if century is None:
            return False
        return _birth_date(century, match_obj) is not None

    @staticmethod
    def parse(id_number: str) -> Optional[ParseResult]:
        """parse the result"""
        match_obj = match_regexp(id_number, NationalRegistrationNumber.METADATA.regexp)
        if not match_obj:
            return None
        century = _century(normalize(id_number))
        if century is None:
            return None
        birth_date = _birth_date(century, match_obj)
        if birth_date is None:
            return None
        sn = match_obj.group('sn')
        return {
            'yyyymmdd': birth_date,
            'gender': Gender.MALE if int(sn) % 2 == 1 else Gender.FEMALE,
            'sn': sn,
            'checksum': int(match_obj.group('checksum'))
        }

    @staticmethod
    def checksum(id_number) -> bool:
        """
        calculated as the remainder of dividing xxxxxxxxxx by 97
        (if the remainder is 0, the check number is set to 97).
        For a person born from 2000 the digit 2 is put in front of the first nine digits.
        """
        if not validate_regexp(id_number, NationalRegistrationNumber.METADATA.regexp):
            return False
        return _century(normalize(id_number)) is not None
