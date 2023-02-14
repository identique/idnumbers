import re
from datetime import date
from math import floor
from types import SimpleNamespace
from typing import Optional, Tuple, TypedDict
from .util import CHECK_DIGIT, validate_regexp
from .constant import Gender


class ParseResult(TypedDict):
    yyyymmdd: date
    """birthday of this ID"""
    gender: Gender
    """only male or female"""
    sn: str
    """serial number"""
    checksum: CHECK_DIGIT
    """checksum digits"""


class PersonalCode:
    """
    Lithuania personal code, asmens kodas
    https://en.wikipedia.org/wiki/National_identification_number#Lithuania
    https://www.oecd.org/tax/automatic-exchange/crs-implementation-and-assistance/tax-identification-numbers/Lithuania-TIN.pdf
    """
    METADATA = SimpleNamespace(**{
        'iso3166_alpha2': 'LT',
        'min_length': 11,
        'max_length': 11,
        'parsable': True,
        'checksum': True,
        'regexp': re.compile(r'^(?P<g>\d)'
                             r'(?P<yy>\d{2})(?P<mm>\d{2})(?P<dd>\d{2})'
                             r'(?P<sn>\d{3})'
                             r'(?P<checksum>\d)$')
    })

    @staticmethod
    def validate(id_number: str) -> bool:
        """
        Validate the Italy fiscal code
        """
        if not id_number:
            return False

        if not isinstance(id_number, str):
            id_number = repr(id_number)
        return PersonalCode.parse(id_number) is not None

    @staticmethod
    def parse(id_number: str) -> Optional[ParseResult]:
        """
        parse the id number
        """
        match_obj = PersonalCode.METADATA.regexp.match(id_number)
        if not match_obj:
            return None

        checksum = PersonalCode.checksum(id_number)
        if checksum is None or str(checksum) != match_obj.group('checksum'):
            return None
        year_base, gender = PersonalCode.extract_year_base_gender(int(match_obj.group('g')))
        yy = int(match_obj.group('yy'))
        mm = int(match_obj.group('mm'))
        dd = int(match_obj.group('dd'))
        try:
            return {
                'yyyymmdd': date(year_base + yy, mm, dd),
                'gender': gender,
                'sn': match_obj.group('sn'),
                'checksum': checksum
            }
        except ValueError:
            return None

    @staticmethod
    def checksum(id_number) -> Optional[CHECK_DIGIT]:
        """
        algorithm https://en.wikipedia.org/wiki/National_identification_number#Lithuania
        """
        if not validate_regexp(id_number, PersonalCode.METADATA.regexp):
            return None
        b = 1
        c = 3
        d = 0
        e = 0
        numbers = [int(char) for char in id_number]
        for number in numbers[:-1]:
            d += number * b
            e += number * c
            b = b + 1 if b < 9 else 1
            c = c + 1 if c < 9 else 1
        d %= 11
        e %= 11
        if d < 10:
            return d
        elif e < 10:
            return e
        else:
            return 0

    @staticmethod
    def extract_year_base_gender(g: CHECK_DIGIT) -> Optional[Tuple[int, Gender]]:
        """
        algorithm: G = floor(year / 100) * 2 - 34 - gender while gender = {female: 0, male: 1}
        if the value is odd -> male, if the value is even -> female
        """
        gender = Gender.FEMALE if g % 2 == 0 else Gender.MALE
        # remove the affect of gender, -1 if it is male otherwise it should be the original value
        year_g = (g // 2) * 2
        year_base = floor((year_g + 34) / 2) * 100
        return year_base, gender


NationalID = PersonalCode
"""alias of FiscalCode"""
