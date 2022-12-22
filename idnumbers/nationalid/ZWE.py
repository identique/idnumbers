import re
from types import SimpleNamespace
from typing import Optional, TypedDict


class ParseResult(TypedDict):
    register_office_code: str
    national_num: str
    check_letter: str
    district_code: str


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
                             r'(?P<check_letter>[A-Z])'
                             r'(?P<district_code>\d{2}$)')
    })

    @staticmethod
    def validate(id_number: str) -> bool:
        """
        Validate the ZWE id number
        """
        if not isinstance(id_number, str):
            id_number = repr(id_number)
        return NationalID.parse(id_number) is not None

    @staticmethod
    def parse(id_number: str) -> Optional[ParseResult]:
        match_obj = NationalID.METADATA.regexp.match(id_number)
        if not match_obj:
            return None
        register_office_code = match_obj.group('register_office_code')
        national_num = match_obj.group('national_num')
        check_letter = match_obj.group('check_letter')
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
                'national_num': national_num,
                'check_letter': check_letter,
                'district_code': district_code
            }

    @staticmethod
    def checksum(id_number) -> bool:
        match_obj = NationalID.METADATA.regexp.match(id_number)
        register_office_code = match_obj.group('register_office_code')
        national_num = match_obj.group('national_num')
        check_letter = match_obj.group('check_letter')
        return NationalID.get_checksum(register_office_code, national_num) == check_letter

    @staticmethod
    def get_checksum(register_office_code: str, national_num: str) -> str:
        """
        https://www.slideshare.net/povonews/zimbabwe-2018-biometric-voters-roll-analysis-pachedu
        page 56 Appendix 2
        """
        remainder = sum(int(d) for d in (register_office_code + national_num)) % 23
        checksum_list = ['Z', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'J', 'K', 'L', 'M', 'N', 'P', 'Q', 'R', 'S', 'T',
                         'V', 'W', 'X', 'Y']
        return checksum_list[remainder]

    @staticmethod
    def check_district_code(code: str) -> bool:
        valid_district_codes = ['02', '03', '04', '05', '06', '07', '08', '10', '11', '12', '13', '14', '15', '18',
                                '19', '21', '22', '23', '24', '25', '26', '27', '28', '29', '32', '34', '35', '37',
                                '38', '39', '41', '42', '43', '44', '45', '46', '47', '48', '49', '50', '53', '54',
                                '56', '58', '59', '61', '63', '66', '67', '68', '70', '71', '73', '75', '77', '79',
                                '80', '83', '84', '85', '86']
        return code in valid_district_codes
