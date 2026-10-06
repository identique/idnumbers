import re
from types import SimpleNamespace
from typing import Optional, TypedDict
from datetime import date

from ..constant import Gender
from ..util import validate_regexp, match_regexp


class ParseResult(TypedDict):
    """parse result of National ID"""
    gender: Gender
    """gender, possible value: male, female"""
    yyyymmdd: date
    """dob"""
    checksum: str
    """checksum, 2 digits"""


class NationalID:
    """
    Norway National ID number
    https://en.wikipedia.org/wiki/National_identification_number#Norway
    https://en.wikipedia.org/wiki/National_identity_number_(Norway)

    Besides the fødselsnummer proper, two variants that keep the 11-digit layout are accepted. Both add 4 to one digit
    of the date, and the control digits are computed over the digits as written
    (https://no.wikipedia.org/wiki/F%C3%B8dselsnummer):

    - D-number (temporary number): 4 is added to the first digit of the day, so the day is 41-71.
    - H-number (hjelpenummer): 4 is added to the third digit, so the month is 41-52.

    A number that has both additions is not a defined type and is invalid. FH-numbers (first digit 8 or 9) carry no
    birth date and are invalid as well.
    """
    METADATA = SimpleNamespace(**{
        'iso3166_alpha2': 'NO',
        # length without insignificant chars
        'min_length': 11,
        'max_length': 11,
        'parsable': True,
        'checksum': True,
        'regexp': re.compile(r'^(?P<dd>\d{2})'
                             r'(?P<mm>\d{2})'
                             r'(?P<yy>\d{2})'
                             r'(?P<individual_number>\d{3})'
                             r'(?P<checksum>\d{2})$'),
        'alias_of': None,
        'names': ['National ID Number',
                  'fødselsnummer',
                  'birth number',
                  'riegádannummir'],
        'links': ['https://en.wikipedia.org/wiki/National_identification_number#Norway',
                  'https://en.wikipedia.org/wiki/National_identity_number_(Norway)',
                  'https://no.wikipedia.org/wiki/F%C3%B8dselsnummer'],
        'deprecated': False
    })

    @staticmethod
    def validate(id_number: str) -> bool:
        """
        Validate the NOR id number
        """
        if not validate_regexp(id_number, NationalID.METADATA.regexp):
            return False
        if not NationalID.parse(id_number):
            return False
        return NationalID.checksum(id_number)

    NUMBER_OFFSET = 40
    D_NUMBER_DAYS = range(41, 72)
    H_NUMBER_MONTHS = range(41, 53)

    @staticmethod
    def parse(id_number: str) -> Optional[ParseResult]:
        """
        parse the result, None if the input is invalid or has no real calendar birth date

        For a D-number or an H-number, yyyymmdd is the real birth date, with the 40 taken off again.
        """
        match_obj = match_regexp(id_number, NationalID.METADATA.regexp)
        if not match_obj:
            return None

        individual_code = match_obj.group('individual_number')
        yy = match_obj.group('yy')
        mm = match_obj.group('mm')
        dd = match_obj.group('dd')

        birth_century = '20'
        individual_num = int(individual_code)
        if 0 <= individual_num < 500:
            birth_century = 19
        elif 500 <= individual_num < 750 and int(yy) >= 54:
            birth_century = 18
        elif 900 <= individual_num < 1000 and int(yy) >= 40:
            birth_century = 19

        day = int(dd)
        month = int(mm)
        is_d_number = day in NationalID.D_NUMBER_DAYS
        is_h_number = month in NationalID.H_NUMBER_MONTHS
        if is_d_number and is_h_number:
            return None
        if is_d_number:
            day -= NationalID.NUMBER_OFFSET
        elif is_h_number:
            month -= NationalID.NUMBER_OFFSET

        try:
            birth_date = date(int(f'{birth_century}{yy}'), month, day)
        except ValueError:
            return None

        return {
            "gender": Gender.FEMALE if int(individual_code[2]) % 2 == 0 else Gender.MALE,
            'yyyymmdd': birth_date,
            "checksum": match_obj.group('checksum')
        }

    FIRST_MAGIC_MULTIPLIER = [3, 7, 6, 1, 8, 9, 4, 5, 2, 1]
    SECOND_MAGIC_MULTIPLIER = [5, 4, 3, 2, 7, 6, 5, 4, 3, 2, 1]

    @staticmethod
    def checksum(id_number: str) -> bool:
        """algorithm: https://en.wikipedia.org/wiki/National_identity_number_(Norway)#Check_digits"""
        if not validate_regexp(id_number, NationalID.METADATA.regexp):
            return False
        number_list = [int(char) for char in id_number]
        # Digit 10th
        first_total = sum([value * number_list[idx] for (idx, value) in enumerate(NationalID.FIRST_MAGIC_MULTIPLIER)])
        # Digit 11th
        second_total = sum([value * number_list[idx] for (idx, value) in enumerate(NationalID.SECOND_MAGIC_MULTIPLIER)])
        return first_total % 11 == 0 and second_total % 11 == 0
