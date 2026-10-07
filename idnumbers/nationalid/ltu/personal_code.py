import re
from datetime import date
from ..metadata import IdMetadata
from typing import Optional, Tuple, TypedDict, cast
from ..constant import Gender
from ..util import CHECK_DIGIT, validate_regexp, match_regexp


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

    The first-digit century mapping for 1-8 follows python-stdnum 2.2's Lithuanian
    module and its shared birth-date decoder (pairs 1/2: 1800s, 3/4: 1900s,
    5/6: 2000s, 7/8: 2100s):

    https://github.com/arthurdejong/python-stdnum/blob/2.2/stdnum/lt/asmens.py
    https://github.com/arthurdejong/python-stdnum/blob/2.2/stdnum/ee/ik.py

    The OECD sheet documents the birth-date structure and two-pass checksum:
    https://www.oecd.org/content/dam/oecd/en/topics/policy-issue-focus/aeoi/lithuania-tin.pdf

    https://en.wikipedia.org/wiki/National_identification_number#Lithuania
    https://www.oecd.org/tax/automatic-exchange/crs-implementation-and-assistance/tax-identification-numbers/Lithuania-TIN.pdf
    """
    METADATA = IdMetadata(**{
        'iso3166_alpha2': 'LT',
        'min_length': 11,
        'max_length': 11,
        'parsable': True,
        'checksum': True,
        'regexp': re.compile(r'^(?P<g>\d)'
                             r'(?P<yy>\d{2})(?P<mm>\d{2})(?P<dd>\d{2})'
                             r'(?P<sn>\d{3})'
                             r'(?P<checksum>\d)$'),
        'alias_of': None,
        'names': ['Personal Code',
                  'asmens kodas'],
        'links': ['https://en.wikipedia.org/wiki/National_identification_number#Lithuania',
                  'https://www.oecd.org/tax/automatic-exchange/crs-implementation-and-assistance/'
                  'tax-identification-numbers/Lithuania-TIN.pdf'],
        'deprecated': False,
        'country_name': 'Lithuania',
        'id_type': 'Personal Code',
        'official_name': 'asmens kodas',
        'display_format': 'GYYMMDDSSSC',
        'example': '39001010077',
        'checksum_algorithm': 'Weighted sum mod 11 in two passes (weights 1-9 and 1; then 3-9, 1, 2 and 3 when the '
                              'remainder is 10; a second 10 becomes 0)',
        'masks': ('###########',)
    })

    @staticmethod
    def validate(id_number: str) -> bool:
        """
        Validate the Lithuania personal code
        """
        if not isinstance(id_number, str) or not id_number:
            return False
        return PersonalCode.parse(id_number) is not None

    @staticmethod
    def parse(id_number: str) -> Optional[ParseResult]:
        """
        parse the id number
        """
        match_obj = match_regexp(id_number, PersonalCode.METADATA.regexp)
        if not match_obj:
            return None

        checksum = PersonalCode.checksum(id_number)
        if checksum is None or str(checksum) != match_obj.group('checksum'):
            return None
        year_base, gender = PersonalCode.extract_year_base_gender(cast(CHECK_DIGIT, int(match_obj.group('g'))))
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
    def checksum(id_number: str) -> Optional[CHECK_DIGIT]:
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
            return cast(CHECK_DIGIT, d)
        elif e < 10:
            return cast(CHECK_DIGIT, e)
        else:
            return 0

    @staticmethod
    def extract_year_base_gender(g: CHECK_DIGIT) -> Tuple[int, Gender]:
        """
        First digits 1/2, 3/4, 5/6 and 7/8 encode the 1800s, 1900s, 2000s and 2100s.
        Odd digits encode male and even digits encode female.
        The historical mapping outside 1-8 is retained for compatibility; this does
        not establish that codes starting with 0 or 9 are government-issued.
        """
        gender = Gender.FEMALE if g % 2 == 0 else Gender.MALE
        if 1 <= g <= 8:
            year_base = 1800 + ((g - 1) // 2) * 100
        else:
            year_base = 1700 + (g // 2) * 100
        return year_base, gender
