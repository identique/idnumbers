import re
from datetime import date
from types import SimpleNamespace
from typing import Optional, Tuple, TypedDict, cast
from .util import CHECK_ALPHA, validate_regexp
from .constant import Gender


class ParseResult(TypedDict):
    """parse result of FiscalCode"""
    surname_consonants: str
    """The 3 consonants chars of surname"""
    firstname_consonants: str
    """The 3 consonants chars of firstname"""
    yyyymmdd: date
    """birthday of this ID"""
    gender: Gender
    """only male or female"""
    area_code: str
    """registry code check the page https://en.wikipedia.org/wiki/Italian_fiscal_code"""
    checksum: CHECK_ALPHA
    """alphabet checksum"""


class FiscalCode:
    """
    Italy fiscal code
    https://en.wikipedia.org/wiki/Italian_fiscal_code
    https://en.wikipedia.org/wiki/National_identification_number#Italy
    """
    METADATA = SimpleNamespace(**{
        'iso3166_alpha2': 'IT',
        'min_length': 16,
        'max_length': 16,
        'parsable': True,
        'checksum': True,
        'regexp': re.compile(r'^(?P<surname>[A-Z]{3})'
                             r'(?P<firstname>[A-Z]{3})'
                             r'(?P<yy>[0-9A-Z]{2})'
                             r'(?P<m>[A-EHLMPR-T])'
                             r'(?P<dd>[0-9A-Z]{2})'
                             r'(?P<area_code>[A-Z][0-9A-Z]{3})'
                             r'(?P<checksum>[A-Z])$')
    })

    MONTH_MAP = {'A': 1, 'B': 2, 'C': 3, 'D': 4,
                 'E': 5, 'H': 6, 'L': 7, 'M': 8,
                 'P': 9, 'R': 10, 'S': 11, 'T': 12}
    """char to month map"""

    MAGIC_ODD_CHAR_MAP = {'0': 1, '9': 21, 'I': 19, 'R': 8,
                          '1': 0, 'A': 1, 'J': 21, 'S': 12,
                          '2': 5, 'B': 0, 'K': 2, 'T': 14,
                          '3': 7, 'C': 5, 'L': 4, 'U': 16,
                          '4': 9, 'D': 7, 'M': 18, 'V': 10,
                          '5': 13, 'E': 9, 'N': 20, 'W': 22,
                          '6': 15, 'F': 13, 'O': 11, 'X': 25,
                          '7': 17, 'G': 15, 'P': 3, 'Y': 24,
                          '8': 19, 'H': 17, 'Q': 6, 'Z': 23}
    """magic numbers for odd chars"""

    MAGIC_EVEN_CHAR_MAP = {'0': 0, '9': 9, 'I': 8, 'R': 17,
                           '1': 1, 'A': 0, 'J': 9, 'S': 18,
                           '2': 2, 'B': 1, 'K': 10, 'T': 19,
                           '3': 3, 'C': 2, 'L': 11, 'U': 20,
                           '4': 4, 'D': 3, 'M': 12, 'V': 21,
                           '5': 5, 'E': 4, 'N': 13, 'W': 22,
                           '6': 6, 'F': 5, 'O': 14, 'X': 23,
                           '7': 7, 'G': 6, 'P': 15, 'Y': 24,
                           '8': 8, 'H': 7, 'Q': 16, 'Z': 25}
    """magic numbers for even chars"""

    NUMERIC_REPLACEMENT = {'L': '0', 'Q': '4', 'U': '8',
                           'M': '1', 'R': '5', 'V': '9',
                           'N': '2', 'S': '6',
                           'P': '3', 'T': '7'}
    """reverse numbers replacement for conflict IDs"""

    @staticmethod
    def validate(id_number: str) -> bool:
        """
        Validate the Italy fiscal code
        """
        if not id_number:
            return False

        if not isinstance(id_number, str):
            id_number = repr(id_number)
        return FiscalCode.parse(id_number) is not None

    @staticmethod
    def parse(id_number: str) -> Optional[ParseResult]:
        """
        parse the id number
        """
        match_obj = FiscalCode.METADATA.regexp.match(id_number)
        if not match_obj:
            return None

        # sterilization from right to left. we need to do the area_code first
        area_code = match_obj.group('area_code')
        sterilized_ac_nums = FiscalCode.sterilize_numbers(area_code[1:])
        if not sterilized_ac_nums:
            return None

        # let the extract_birthday to sterilize others
        dob_gender = FiscalCode.extract_birthday(match_obj.group('yy'),
                                                 match_obj.group('m'),
                                                 match_obj.group('dd'))
        if dob_gender is None:
            return None

        checksum = FiscalCode.checksum(id_number)
        if checksum is None or str(checksum) != match_obj.group('checksum'):
            return None

        return {
            'surname_consonants': match_obj.group('surname'),
            'firstname_consonants': match_obj.group('firstname'),
            'area_code': area_code[0] + sterilized_ac_nums,
            'yyyymmdd': dob_gender[0],
            'gender': dob_gender[1],
            'checksum': checksum
        }

    @staticmethod
    def checksum(id_number) -> Optional[CHECK_ALPHA]:
        """
        build the checksum after the sterilization
        """
        if not validate_regexp(id_number, FiscalCode.METADATA.regexp):
            return None
        odd_total = 0
        even_total = 0
        alphanum = id_number[:-1]
        for index, char in enumerate(alphanum):
            if (index + 1) % 2 == 1:
                odd_total += FiscalCode.MAGIC_ODD_CHAR_MAP[char]
            else:
                even_total += FiscalCode.MAGIC_EVEN_CHAR_MAP[char]
        modulus = (odd_total + even_total) % 26
        return cast(CHECK_ALPHA, chr(65 + modulus))

    @staticmethod
    def extract_birthday(yy_str: str, m: str, dd_str: str) -> Optional[Tuple[date, Gender]]:
        """sterilize the numbers and convert the str to DoB and gender"""
        if m not in FiscalCode.MONTH_MAP:
            return None
        sterilized_dd = FiscalCode.sterilize_numbers(dd_str)
        if not sterilized_dd:
            return None
        sterilized_yy = FiscalCode.sterilize_numbers(yy_str)
        if not sterilized_yy:
            return None
        yy = int(sterilized_yy)
        dd = int(sterilized_dd)
        year_base = 2000 if yy < 50 else 1900
        mm = FiscalCode.MONTH_MAP[m]
        day = dd if dd < 40 else dd - 40
        gender = Gender.MALE if dd < 40 else Gender.FEMALE
        try:
            return date(year_base + yy, mm, day), gender
        except ValueError:
            return None

    @staticmethod
    def sterilize_numbers(source: str) -> Optional[str]:
        """
        When the id is conflict with others, it replaces numbers to char. We need to reverse them.
        """
        result = ''
        for char in list(source[::-1]):
            if ord(char) > 64:
                if char not in FiscalCode.NUMERIC_REPLACEMENT:
                    return None
                result += char
            else:
                result += char

        return result[::-1]


NationalID = FiscalCode
"""alias of FiscalCode"""
