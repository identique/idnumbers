import re
from datetime import date
from types import SimpleNamespace
from typing import Optional, Pattern, TypedDict
from ..constant import Gender
from ..util import validate_regexp, luhn_digit, match_regexp


def normalize(id_number: str) -> str:
    """strip out useless characters/whitespaces"""
    return re.sub(r'[+-]', '', id_number)


class ParseResult(TypedDict):
    """parse result of PersonalIdentityNumber"""
    gender: Gender
    """gender, possible value: male, female"""
    yyyymmdd: date
    """dob"""
    checksum: str
    """checksum digit"""


class PersonalIdentityNumber:
    """
    Sweden Personal Identity number.

    Accepts 10 or 12 digits, with an optional ``-`` or ``+`` before the last four digits.
    An explicit four-digit year determines the century regardless of the separator.
    For a two-digit year, ``+`` denotes the older century; compact input is treated as ``-``.
    Validation checks syntax, calendar date and checksum, not issuance or identity status.

    Skatteverket describes personnummer and the twelve-digit database format:
    https://www.skatteverket.se/privat/folkbokforing/personnummer.4.3810a01c150939e893f18c29.html
    https://www4.skatteverket.se/rattsligvagledning/edition/2026.12/330242.html
    https://en.wikipedia.org/wiki/National_identification_number#Sweden
    https://en.wikipedia.org/wiki/Personal_identity_number_(Sweden%29
    https://swedish.identityinfo.net/
    https://personnummer.dev/
    """
    METADATA = SimpleNamespace(**{
        'iso3166_alpha2': 'SE',
        # length without insignificant chars
        'min_length': 10,
        'max_length': 12,
        'parsable': True,
        'checksum': True,
        'regexp': re.compile(r'^(?P<century>[0-9]{2})?(?P<yy>[0-9]{2})(?P<mm>[0-9]{2})(?P<dd>[0-9]{2})'
                             r'(?P<sep>[+-])?'
                             r'(?!000)(?P<birth_number>[0-9]{3})'
                             r'(?P<checksum>[0-9])$'),
        'alias_of': None,
        'names': ['Personal Identity Number',
                  'personnummer'],
        'links': ['https://www.skatteverket.se/privat/folkbokforing/personnummer.4.3810a01c150939e893f18c29.html',
                  'https://www4.skatteverket.se/rattsligvagledning/edition/2026.12/330242.html',
                  'https://en.wikipedia.org/wiki/National_identification_number#Sweden',
                  'https://en.wikipedia.org/wiki/Personal_identity_number_(Sweden)',
                  'https://swedish.identityinfo.net/',
                  'https://personnummer.dev/'],
        'deprecated': False

    })

    @staticmethod
    def validate(id_number: str) -> bool:
        """
        Validate the SWE id number
        """
        if not validate_regexp(id_number, PersonalIdentityNumber.METADATA.regexp):
            return False
        return PersonalIdentityNumber.parse(id_number) is not None

    @staticmethod
    def parse(id_number: str) -> Optional[ParseResult]:
        return _parse(id_number, PersonalIdentityNumber.METADATA.regexp)

    @staticmethod
    def checksum(id_number: str) -> Optional[int]:
        """
        algorithm: https://en.wikipedia.org/wiki/Personal_identity_number_(Sweden%29#Checksum
        Multiplier start by 2
        """
        return _checksum(id_number, PersonalIdentityNumber.METADATA.regexp)


def _checksum(id_number: str, regexp: Pattern[str]) -> Optional[int]:
    """Calculate from the encoded YYMMDD and serial, excluding any century digits."""
    if not validate_regexp(id_number, regexp):
        return None
    normalized = normalize(id_number)
    return luhn_digit([int(char) for char in normalized[-10:-1]], True)


def _parse(id_number: str, regexp: Pattern[str], day_offset: int = 0) -> Optional[ParseResult]:
    """Share format, century and gender decoding between Sweden's two number types."""
    match_obj = match_regexp(id_number, regexp)
    if not match_obj:
        return None
    checksum = match_obj.group('checksum')
    if _checksum(id_number, regexp) != int(checksum):
        return None
    yy = int(match_obj.group('yy'))
    century = match_obj.group('century')
    if century is not None:
        yyyy = int(century) * 100 + yy
    else:
        # Keep the legacy two-digit +/- century calculation; compact input means '-'.
        base_year = date.today().year - (100 if match_obj.group('sep') == '+' else 0)
        yyyy = int((base_year - ((base_year - yy) % 100)) / 100) * 100 + yy
    try:
        return {
            'gender': Gender.FEMALE if int(match_obj.group('birth_number')) % 2 == 0 else Gender.MALE,
            'yyyymmdd': date(yyyy, int(match_obj.group('mm')), int(match_obj.group('dd')) - day_offset),
            'checksum': checksum
        }
    except ValueError:
        return None
