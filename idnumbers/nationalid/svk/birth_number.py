import re
from datetime import date
from typing import Optional, TypedDict
from types import SimpleNamespace

from ..constant import Gender
from ..util import CHECK_DIGIT, validate_regexp, match_regexp


class BirthNumberParseResult(TypedDict):
    yyyymmdd: date
    """birthday of this ID, there is no way to know the century of the birthday. So, yy < 50 is 20yy else 19yy."""
    gender: Gender
    """only male or female"""
    sn: str
    """serial number"""
    checksum: CHECK_DIGIT
    """checksum"""


class BirthNumber:
    """
    Slovakia Birth Number format, rodné číslo (RČ)
    https://en.wikipedia.org/wiki/National_identification_number#Slovakia

    The Czech Republic uses the same system, so ``CZE.BirthNumber`` is a subclass of this class.

    Check digit: the 10th digit is the remainder of the first nine digits divided by 11. When that
    remainder is 10 the check digit is 0, so such a number is *not* divisible by 11 as a whole
    (this was used for about 1,000 numbers per year until 1985). Every other number is divisible by 11.

    Sources: Czech Wikipedia "Rodné číslo" (citing law no. 133/2000 Sb.) and python-stdnum
    ``stdnum/cz/rc.py``, which checks ``int(number[:9]) % 11 % 10``.
    """
    METADATA = SimpleNamespace(**{
        'iso3166_alpha2': 'SK',
        'min_length': 10,
        'max_length': 10,
        # length without insignificant chars
        'parsable': True,
        # has parse function
        'checksum': True,
        # has checksum function
        'regexp': re.compile(r'^(?P<yy>\d{2})'
                             r'(?P<mm>\d{2})'
                             r'(?P<dd>\d{2})/?'
                             r'(?P<sn>\d{3})'
                             r'(?P<checksum>\d)$'),
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
        Validate birth number
        """
        if not validate_regexp(id_number, BirthNumber.METADATA.regexp):
            return False
        return BirthNumber.parse(id_number) is not None

    @staticmethod
    def parse(id_number: str) -> Optional[BirthNumberParseResult]:
        """
        parse the id number
        """
        match_obj = match_regexp(id_number, BirthNumber.METADATA.regexp)
        if not match_obj:
            return None

        if not BirthNumber.checksum(id_number):
            return None

        yy = int(match_obj.group('yy'))
        mm_code = int(match_obj.group('mm'))
        dd = int(match_obj.group('dd'))
        mm = mm_code if mm_code < 50 else mm_code - 50
        """
        from https://en.wikipedia.org/wiki/National_identification_number#Czech_Republic_and_Slovakia
        In a law that took place in the year 2004, a failsafe system has been implemented, where in case
        all valid serial numbers get depleted for a day, the number 20 gets added to the value of XX.
        This means that XX can get up to 32 for males, and 82 for females.
        """
        mm = mm - 20 if mm > 20 else mm
        year_base = 2000 if yy < 50 else 1900
        try:
            return {
                'yyyymmdd': date(year_base + yy, mm, dd),
                'gender': Gender.MALE if mm_code < 50 else Gender.FEMALE,
                'sn': match_obj.group('sn'),
                'checksum': int(match_obj.group('checksum'))
            }
        except ValueError:
            return None

    @staticmethod
    def checksum(id_number: str) -> bool:
        """
        Check the check digit: it is ``int(first nine digits) % 11 % 10``.

        This is the same as "the whole number is divisible by 11", except when the first nine digits
        leave remainder 10: the check digit is then 0, and the whole number is not divisible by 11.
        """
        if not validate_regexp(id_number, BirthNumber.METADATA.regexp):
            return False
        digits = BirthNumber.normalize(id_number)
        return int(digits[:9]) % 11 % 10 == int(digits[9])

    @staticmethod
    def normalize(id_number: str) -> str:
        """remove the / out"""
        return re.sub(r'/', '', id_number)
