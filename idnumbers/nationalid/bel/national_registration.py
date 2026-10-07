import calendar
import re
from datetime import date
from ..metadata import IdMetadata
from typing import Optional, Tuple, TypedDict
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


def _is_valid_birth_date(century: int, match_obj: re.Match[str]) -> bool:
    """
    Check the birth date part, which may be incomplete.

    A month of 00 (only the year is known, or the day counter of an unknown month ran out) is valid
    with any day. A valid month with the day 00 is valid too. Otherwise the day must exist in that month
    of the inferred century (IT000; python-stdnum stdnum/be/nn.py).
    """
    year = century + int(match_obj.group('yy'))
    month = int(match_obj.group('mm'))
    day = int(match_obj.group('dd'))
    if month == 0:
        return True
    if month > 12:
        return False
    return day <= calendar.monthrange(year, month)[1]


def _match_valid(id_number: str) -> Optional[Tuple[int, re.Match[str]]]:
    """
    Match the number against the regexp and check the century and the birth date part.

    :param id_number: the national registration number, with or without separators
    :return: the century and the regexp match, or None if the format, the check digits or the birth date is invalid
    """
    match_obj = match_regexp(id_number, NationalRegistrationNumber.METADATA.regexp)
    if not match_obj:
        return None
    century = _century(normalize(id_number))
    if century is None:
        return None
    if not _is_valid_birth_date(century, match_obj):
        return None
    return century, match_obj


class NationalRegistrationNumber:
    """
    Belgium National register number format
    https://en.wikipedia.org/wiki/Belgian_identity_card

    The number is the birth date (``yymmdd``), a 3-digit serial number (odd for men, even for women)
    and 2 check digits. The check digits are ``97 - (the first nine digits mod 97)``; for a person
    born from 2000 the digit 2 is put in front of the nine digits. The century of birth can therefore
    only be found by computing the check digits, and ``parse()`` returns the century that matches.
    A 20xx birth year in the future is not accepted.

    The birth date may be incomplete: when only the year, or the year and month, were known, the
    unknown parts are zeroes (for example ``40 00 00 953 81``), and when that serial range runs out
    the day counts up from 01 with the month still 00. A number with an unknown birth date uses the
    fictitious date 00 00 01. Such a number is valid, so ``validate()`` is True, but ``parse()``
    returns None because there is no complete birth date to put in ``yyyymmdd``.
    A day that does not exist in its month (for example 30 February) is still invalid.

    Bis numbers (month + 20 or + 40) are a different ID type and are not supported.

    Sources: the official Rijksregister instruction IT000 "Het identificatienummer" (15.05.2016)
    and python-stdnum ``stdnum/be/nn.py``.
    """
    METADATA = IdMetadata(**{
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
                  'https://www.checkdoc.be/CheckDoc/homepage.do',
                  'https://www.ibz.rrn.fgov.be/sites/default/files/documents/nl/rijksregister/onderrichtingen/'
                  'IT-lijst/IT000_Rijksregisternummer.pdf'],
        'deprecated': False
    })

    @staticmethod
    def validate(id_number: str) -> bool:
        """validate the id"""
        return _match_valid(id_number) is not None

    @staticmethod
    def parse(id_number: str) -> Optional[ParseResult]:
        """parse the result"""
        matched = _match_valid(id_number)
        if matched is None:
            return None
        century, match_obj = matched
        yy = int(match_obj.group('yy'))
        mm = int(match_obj.group('mm'))
        dd = int(match_obj.group('dd'))
        if mm == 0 or dd == 0:
            # incomplete birth date: the number is valid, but there is no date to return
            return None
        sn = match_obj.group('sn')
        return {
            'yyyymmdd': date(century + yy, mm, dd),
            'gender': Gender.MALE if int(sn) % 2 == 1 else Gender.FEMALE,
            'sn': sn,
            'checksum': int(match_obj.group('checksum'))
        }

    @staticmethod
    def checksum(id_number: str) -> bool:
        """
        calculated as the remainder of dividing xxxxxxxxxx by 97
        (if the remainder is 0, the check number is set to 97).
        For a person born from 2000 the digit 2 is put in front of the first nine digits.
        """
        if not validate_regexp(id_number, NationalRegistrationNumber.METADATA.regexp):
            return False
        return _century(normalize(id_number)) is not None
