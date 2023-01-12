import datetime
import re
from types import SimpleNamespace
from .util import validate_regexp, luhn_digit
from typing import Optional, TypedDict
from .constant import Gender


def normalize(id_number):
    return re.sub(r'[+-]', '', id_number)


class ParseResult(TypedDict):
    gender: Gender
    yyyymmdd: datetime.date
    checksum: str


class PersonalIdentityNumber:
    """
    Sweden Personal Identity number
    https://en.wikipedia.org/wiki/National_identification_number#Sweden
    https://en.wikipedia.org/wiki/Personal_identity_number_(Sweden)
    https://swedish.identityinfo.net/
    https://personnummer.dev/
    """
    METADATA = SimpleNamespace(**{
        'iso3166_alpha2': 'SE',
        # length without insignificant chars
        'min_length': 10,
        'max_length': 10,
        'parsable': True,
        'checksum': True,
        'regexp': re.compile(r'^(?P<yy>\d{2})(?P<mm>\d{2})(?P<dd>\d{2})'
                             r'(?P<sep>[+|-])'
                             r'(?!000)(?P<birth_number>\d{3})'
                             r'(?P<checksum>\d)$')

    })

    @staticmethod
    def validate(id_number: str) -> bool:
        """
        Validate the SWE id number
        """
        if not validate_regexp(id_number, PersonalIdentityNumber.METADATA.regexp):
            return False
        return PersonalIdentityNumber.parse(id_number) is not None

    @staticmethod
    def parse(id_number: str) -> Optional[ParseResult]:
        match_obj = PersonalIdentityNumber.METADATA.regexp.match(id_number)
        if not match_obj:
            return None
        yy = match_obj.group('yy')
        mm = match_obj.group('mm')
        dd = match_obj.group('dd')
        birth_number = match_obj.group('birth_number')
        sep = match_obj.group('sep')
        base_year = datetime.datetime.now().year if sep == '-' else datetime.datetime.now().year - 100
        yyyy = int((base_year - ((base_year - int(yy)) % 100)) / 100) * 100 + int(yy)
        checksum = match_obj.group('checksum')
        if PersonalIdentityNumber.checksum(id_number) != int(checksum):
            return None
        return {
            "gender": Gender.FEMALE if int(birth_number) % 2 == 0 else Gender.MALE,
            "yyyymmdd": datetime.date(yyyy, int(mm), int(dd)),
            'checksum': match_obj.group('checksum')
        }

    @staticmethod
    def checksum(id_number: str) -> int:
        normalized = normalize(id_number)
        '''
        https://en.wikipedia.org/wiki/Personal_identity_number_(Sweden)#Checksum
        Multiplier start by 2
        '''
        return luhn_digit([int(char) for char in normalized[:-1]], True)
