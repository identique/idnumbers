import re
from datetime import date
from types import SimpleNamespace
from typing import Optional, TypedDict, Tuple
from .util import CHECK_DIGIT, weighted_modulus_digit, validate_regexp
from .constant import Citizenship, Gender


class ParseResult(TypedDict):
    """
    parse result of JMBG
    """
    yyyymmdd: date
    """date of birth"""
    location: str
    """birth location"""
    citizenship: Citizenship
    """citizenship of Slovenia"""
    gender: Gender
    """gender, male or female"""
    sn: str
    """serial"""
    checksum: CHECK_DIGIT
    """checksum digit"""


class UniqueMasterCitizenNumber:
    """
    Yugoslavia JMBG which is shared among all independent countries from Yugoslavia.
    https://en.wikipedia.org/wiki/Unique_Master_Citizen_Number
    """
    METADATA = SimpleNamespace(**{
        'iso3166_alpha2': None,
        'min_length': 13,
        'max_length': 13,
        'parsable': True,
        'checksum': True,
        'regexp': re.compile(r'^(?P<dd>\d{2})'
                             r'(?P<mm>\d{2})'
                             r'(?P<yyy>\d{3})'
                             r'(?P<location>\d{2})'
                             r'(?P<sn>\d{3})'
                             r'(?P<checksum>\d)$')
    })

    MAGIC_MULTIPLIER = [7, 6, 5, 4, 3, 2]
    """multiplier for checksum"""

    LOC_BLACK_LIST = ['20', '40', '51', '52', '53', '54', '55', '56', '57', '58', '59', '90', '97', '98', '99']

    @staticmethod
    def validate(id_number: str) -> bool:
        """
        Validate the JMBG id number
        """
        if not validate_regexp(id_number, UniqueMasterCitizenNumber.METADATA.regexp):
            return False
        return UniqueMasterCitizenNumber.parse(id_number) is not None

    @staticmethod
    def parse(id_number: str) -> Optional[ParseResult]:
        """parse the value"""
        match_obj = UniqueMasterCitizenNumber.METADATA.regexp.match(id_number)
        if not match_obj:
            return None
        checksum = UniqueMasterCitizenNumber.checksum(id_number)
        if not checksum:
            return None
        loc_citizenship = UniqueMasterCitizenNumber.check_location(match_obj.group('location'))
        if not loc_citizenship:
            return None
        citizenship, location = loc_citizenship
        yyy = int(match_obj.group('yyy'))
        mm = int(match_obj.group('mm'))
        dd = int(match_obj.group('dd'))
        year_base = 2000 if yyy < 800 else 1000
        sn = match_obj.group('sn')
        try:
            return {
                'yyyymmdd': date(year_base + yyy, mm, dd),
                'location': location,
                'citizenship': citizenship,
                'gender': Gender.MALE if int(sn) < 500 else Gender.FEMALE,
                'sn': sn,
                'checksum': int(match_obj.group('checksum'))
            }
        except ValueError:
            return None

    @staticmethod
    def checksum(id_number) -> bool:
        """
        algorithm:
        https://en.wikipedia.org/wiki/Unique_Master_Citizen_Number#Checksum_calculation
        """
        if not validate_regexp(id_number, UniqueMasterCitizenNumber.METADATA.regexp):
            return False
        numbers = [int(char) for char in id_number]
        # fold the first 12 digits
        folded = []
        for idx in range(6):
            folded.append(numbers[idx] + numbers[idx + 6])
        # it uses modulus 10 algorithm with magic numbers
        modulus = weighted_modulus_digit(folded, UniqueMasterCitizenNumber.MAGIC_MULTIPLIER, 11)
        if modulus > 9:
            modulus = 0
        return modulus == numbers[-1]

    @staticmethod
    def check_location(location: str) -> Optional[Tuple[Citizenship, str]]:
        """
        Check location with the list from here
        https://en.wikipedia.org/wiki/Unique_Master_Citizen_Number#Composition
        """
        if location in UniqueMasterCitizenNumber.LOC_BLACK_LIST:
            return None
        return Citizenship.CITIZEN, location
