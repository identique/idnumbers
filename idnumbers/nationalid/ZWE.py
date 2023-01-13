import re
from types import SimpleNamespace
from typing import Optional, TypedDict
from .util import validate_regexp


class ParseResult(TypedDict):
    """Parse result of Zimbabwe national identity code"""
    register_office_code: str
    """Register office code"""
    checksum: str
    """Checksum code"""
    district_code: str
    """Code of the district"""


class NationalID:
    """
    Zimbabwe National ID number format
    https://en.wikipedia.org/wiki/National_identification_number#Zimbabwe
    """
    METADATA = SimpleNamespace(**{
        'iso3166_alpha2': 'ZW',
        'min_length': 11,
        'max_length': 12,
        'parsable': True,
        'checksum': True,
        'regexp': re.compile(r'^(?P<register_office_code>\d{2})'
                             r'(?P<national_num>(\d{6}|\d{7}))'
                             r'(?P<checksum>[A-Z])'
                             r'(?P<district_code>\d{2}$)')
    })

    @staticmethod
    def validate(id_number: str) -> bool:
        """
        Validate the ZWE id number
        """
        if not validate_regexp(id_number, NationalID.METADATA.regexp):
            return False
        elif NationalID.parse(id_number) is None:
            return False
        return NationalID.checksum(id_number)

    @staticmethod
    def parse(id_number: str) -> Optional[ParseResult]:
        """parse the ZWE national id"""
        match_obj = NationalID.METADATA.regexp.match(id_number)
        if not match_obj:
            return None
        register_office_code = match_obj.group('register_office_code')
        checksum = match_obj.group('checksum')
        district_code = match_obj.group('district_code')
        if not NationalID.checksum(id_number):
            return None
        elif not NationalID.check_district_code(register_office_code):
            return None
        # 00 is valid district code for foreigner
        elif not NationalID.check_district_code(district_code) and district_code != '00':
            return None
        else:
            return {
                'register_office_code': register_office_code,
                'checksum': checksum,
                'district_code': district_code
            }

    @staticmethod
    def checksum(id_number) -> bool:
        """Validate checksum"""
        match_obj = NationalID.METADATA.regexp.match(id_number)
        register_office_code = match_obj.group('register_office_code')
        national_num = match_obj.group('national_num')
        checksum_code = match_obj.group('checksum')
        return NationalID.get_checksum(register_office_code, national_num) == checksum_code

    @staticmethod
    def get_checksum(register_office_code: str, national_num: str) -> str:
        """
        Implement the checksum rule by
        https://www.slideshare.net/povonews/zimbabwe-2018-biometric-voters-roll-analysis-pachedu
        page 56 Appendix 2
        """
        remainder = sum(int(d) for d in (register_office_code + national_num)) % 23
        checksum_list = ['Z', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'J', 'K', 'L', 'M', 'N', 'P', 'Q', 'R', 'S', 'T',
                         'V', 'W', 'X', 'Y']
        return checksum_list[remainder]

    @staticmethod
    def check_district_code(code: str) -> bool:
        """Map the district code"""
        valid_district_codes = ['02', '03', '04', '05', '06', '07', '08', '10', '11', '12', '13', '14', '15', '18',
                                '19', '21', '22', '23', '24', '25', '26', '27', '28', '29', '32', '34', '35', '37',
                                '38', '39', '41', '42', '43', '44', '45', '46', '47', '48', '49', '50', '53', '54',
                                '56', '58', '59', '61', '63', '66', '67', '68', '70', '71', '73', '75', '77', '79',
                                '80', '83', '84', '85', '86']
        return code in valid_district_codes
