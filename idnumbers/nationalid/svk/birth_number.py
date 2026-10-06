import re
from datetime import date
from re import Match
from typing import Optional, TypedDict
from types import SimpleNamespace

from ..constant import Gender
from ..util import CHECK_DIGIT, validate_regexp, match_regexp


class BirthNumberParseResult(TypedDict):
    yyyymmdd: date
    """
    birthday of this ID. The number has 10 digits only from 1954, so the century follows from that:
    yy < 54 is 20yy else 19yy. A birthday after today is not valid.
    """
    gender: Gender
    """only male or female"""
    sn: str
    """serial number"""
    checksum: CHECK_DIGIT
    """checksum"""


def _birth_date(match_obj: Match[str]) -> Optional[date]:
    """
    Birth date of a matched birth number, or None when the date is not possible.

    from https://en.wikipedia.org/wiki/National_identification_number#Czech_Republic_and_Slovakia
    In a law that took place in the year 2004, a failsafe system has been implemented, where in case
    all valid serial numbers get depleted for a day, the number 20 gets added to the value of XX.
    This means that XX can get up to 32 for males, and 82 for females.
    """
    yy = int(match_obj.group('yy'))
    mm_code = int(match_obj.group('mm'))
    dd = int(match_obj.group('dd'))
    mm = mm_code if mm_code < 50 else mm_code - 50
    mm = mm - 20 if mm > 20 else mm
    if match_obj.group('checksum') is None:
        # 9-digit numbers were only given out up to 1953, so the year is always 19yy
        if yy > 53:
            return None
        year = 1900 + yy
    else:
        # 10-digit numbers exist from 1954 only, so yy 00-53 is 2000-2053 and 54-99 is 1954-1999
        year = (2000 if yy < 54 else 1900) + yy
    try:
        birth_date = date(year, mm, dd)
    except ValueError:
        return None
    return birth_date if birth_date <= date.today() else None


class BirthNumber:
    """
    Slovakia Birth Number format, rodné číslo (RČ)
    https://en.wikipedia.org/wiki/National_identification_number#Slovakia

    The Czech Republic uses the same system, so ``CZE.BirthNumber`` is a subclass of this class.

    Check digit: the 10th digit is the remainder of the first nine digits divided by 11. When that
    remainder is 10 the check digit is 0, so such a number is *not* divisible by 11 as a whole
    (this was used for about a thousand numbers in total, until 1985). Every other number is divisible by 11.

    Century: a 10-digit number only exists from 1954, so ``yy`` 54-99 is 1954-1999 and ``yy`` 00-53 is
    2000-2053. A birth date after today is impossible, so such a number is not valid (this also rejects
    10-digit numbers with ``yy`` 50-53 that used to be read as 1950-1953). The month offsets are +50 for
    women and, since 2004, +20 when the serial numbers of a day run out; the +20 is accepted for any year.

    9-digit form: numbers given out up to and including 1953 have 9 digits (the date, a 3-digit serial
    number and no check digit); people who hold them are still alive. The 9-digit form is only valid for
    a birth year 1900-1953 (``yy <= 53``) with a real calendar date, and has nothing to check, so
    ``checksum()`` is True for any well-formed 9-digit number and the year and date rules are applied by
    ``validate()`` and ``parse()``. The ``checksum`` group of the regexp is absent for a 9-digit number.
    ``parse()`` returns None for a 9-digit number, because the result has a ``checksum`` digit that
    does not exist: ``validate()`` is True while ``parse()`` is None, as for the Belgian number with an
    incomplete birth date.

    Sources: Czech Wikipedia "Rodné číslo" (citing law no. 133/2000 Sb.) and python-stdnum
    ``stdnum/cz/rc.py``, which checks ``int(number[:9]) % 11 % 10`` for 10 digits and accepts 9 digits
    only up to 1953.
    """
    METADATA = SimpleNamespace(**{
        'iso3166_alpha2': 'SK',
        'min_length': 9,
        'max_length': 10,
        # length without insignificant chars: 9 digits before 1954 (no check digit), 10 digits since
        'parsable': True,
        # has parse function
        'checksum': True,
        # has checksum function
        'regexp': re.compile(r'^(?P<yy>\d{2})'
                             r'(?P<mm>\d{2})'
                             r'(?P<dd>\d{2})/?'
                             r'(?P<sn>\d{3})'
                             r'(?P<checksum>\d)?$'),
        # regular expression to validate the id
        'alias_of': None,
        'names': ['Birth Number',
                  'rodné číslo',
                  'RČ'],
        'links': ['https://en.wikipedia.org/wiki/National_identification_number#Slovakia',
                  'https://cs.wikipedia.org/wiki/Rodn%C3%A9_%C4%8D%C3%ADslo',
                  'https://github.com/arthurdejong/python-stdnum/blob/master/stdnum/cz/rc.py'],
        'deprecated': False
    })

    @staticmethod
    def validate(id_number: str) -> bool:
        """
        Validate birth number: the check digit (10 digits only) and the birth date must be right.
        """
        match_obj = match_regexp(id_number, BirthNumber.METADATA.regexp)
        if not match_obj or not BirthNumber.checksum(id_number):
            return False
        return _birth_date(match_obj) is not None

    @staticmethod
    def parse(id_number: str) -> Optional[BirthNumberParseResult]:
        """
        parse the id number. A valid 9-digit number (before 1954) has no check digit to return, so None
        is returned for it, although ``validate()`` is True.
        """
        match_obj = match_regexp(id_number, BirthNumber.METADATA.regexp)
        if not match_obj or match_obj.group('checksum') is None:
            return None

        if not BirthNumber.checksum(id_number):
            return None

        birth_date = _birth_date(match_obj)
        if birth_date is None:
            return None
        return {
            'yyyymmdd': birth_date,
            'gender': Gender.MALE if int(match_obj.group('mm')) < 50 else Gender.FEMALE,
            'sn': match_obj.group('sn'),
            'checksum': int(match_obj.group('checksum'))
        }

    @staticmethod
    def checksum(id_number: str) -> bool:
        """
        Check the check digit: it is ``int(first nine digits) % 11 % 10``.

        This is the same as "the whole number is divisible by 11", except when the first nine digits
        leave remainder 10: the check digit is then 0, and the whole number is not divisible by 11.

        A 9-digit number (before 1954) has no check digit, so there is nothing that can fail and the
        result is True for any well-formed 9-digit number.
        """
        if not validate_regexp(id_number, BirthNumber.METADATA.regexp):
            return False
        digits = BirthNumber.normalize(id_number)
        if len(digits) == 9:
            return True
        return int(digits[:9]) % 11 % 10 == int(digits[9])

    @staticmethod
    def normalize(id_number: str) -> str:
        """remove the / out"""
        return re.sub(r'/', '', id_number)
