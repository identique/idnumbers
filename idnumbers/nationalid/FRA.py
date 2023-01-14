import re
from types import SimpleNamespace
from typing import Optional, TypedDict
from .util import validate_regexp
from .constant import Gender


class BirthDepartment(TypedDict):
    """the commune of origin"""
    department: str
    city: str
    country: str


class ParseResult(TypedDict):
    """parse result of INSEE"""
    gender: Gender
    """gender, possible value: male, female"""
    yy: str
    """year of birth"""
    mm: str
    """month of birth"""
    birth_department: BirthDepartment
    """the commune of origin"""
    checksum: str
    """checksum string"""


class INSEE:
    """
    France National ID number, INSEE
    https://en.wikipedia.org/wiki/National_identification_number#France
    https://fr.wikipedia.org/wiki/Num%C3%A9ro_de_s%C3%A9curit%C3%A9_sociale_en_France#Signification_des_chiffres_du_NIR
    """
    METADATA = SimpleNamespace(**{
        'iso3166_alpha2': 'FR',
        # length without insignificant chars
        'min_length': 15,
        'max_length': 15,
        'parsable': True,
        'checksum': True,
        'regexp': re.compile(r'^(?P<gender>([123478]))'
                             r'(?P<yy>\d{2})'
                             r'(?P<mm>(0[1-9]|1[0-2]|[2-3][0-9]|4[0-2]|[5-9][0-9]))'
                             r'(?P<birth_department>((\d{2}|2[AaBb])\d{3}))'
                             r'(?P<cert_number>((?!000)\d{3}))'
                             r'(?P<control_key>((?!(00|98|99))\d{2}))$')

    })

    @staticmethod
    def validate(id_number: str) -> bool:
        """
        Validate the FRA id number
        """
        if not validate_regexp(id_number, INSEE.METADATA.regexp):
            return False
        if not INSEE.parse(id_number):
            return False
        return INSEE.checksum(id_number)

    @staticmethod
    def parse(id_number: str) -> Optional[ParseResult]:
        match_obj = INSEE.METADATA.regexp.match(id_number)
        if not match_obj:
            return None
        birth_department = INSEE.validate_birth_department(match_obj.group('birth_department'))
        if not birth_department:
            return None
        gender = match_obj.group('gender')
        yy = match_obj.group('yy')
        mm = match_obj.group('mm')
        control_key = match_obj.group('control_key')
        return {
            'gender': Gender.MALE if gender == '1' else Gender.FEMALE,
            'yy': yy,
            'mm': mm,
            'birth_department': birth_department,
            'checksum': control_key,
        }

    @staticmethod
    def checksum(id_number: str) -> bool:
        """algorithm: https://en.wikipedia.org/wiki/INSEE_code#National_identification_numbers"""
        normalized = id_number.upper().replace('2A', '19').replace('2B', '18')
        return 97 - int(normalized[:-2]) % 97 == int(normalized[-2:])

    @staticmethod
    def validate_birth_department(birth_department: str) -> Optional[BirthDepartment]:
        department_code = birth_department[:2].upper()
        if (department_code.isdigit() and 1 <= int(department_code) <= 95) or department_code in ['2A', '2B']:
            return {
                "department": birth_department[:2],
                "city": birth_department[2:],
                "country": ""
            }
        if 97 <= int(department_code) <= 98:
            return {
                "department": birth_department[:3],
                "city": birth_department[3:],
                "country": ""
            }
        if department_code == '99':
            return {
                "department": '',
                "city": '',
                "country": birth_department[2:]
            }
        return None


NationalID = INSEE
