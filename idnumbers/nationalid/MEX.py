import re
from datetime import date
from types import SimpleNamespace
from typing import Literal, Optional, TypedDict
from .util import validate_regexp
from .constant import Gender


class ParseResult(TypedDict):
    """The parse result of CURP"""
    name_initial_chars: str
    """initial chars of name"""
    name_consonants: str
    """consonants of name"""
    yyyymmdd: date
    """dob"""
    gender: Gender
    """gender, possible value: male, female, non-binary"""
    location: str
    """registration location"""
    sn: str
    """serial number"""
    checksum: Literal[0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    """check digit"""


class CURP:
    """
    Mexico National ID number format, CURP
    https://en.wikipedia.org/wiki/Unique_Population_Registry_Code
    http://sistemas.uaeh.edu.mx/dce/admisiones/docs/guia_CURP.pdf
    python version of https://github.com/d3249/curp
    """
    METADATA = SimpleNamespace(**{
        'iso3166_alpha2': 'MX',
        'min_length': 18,
        'max_length': 18,
        'parsable': True,
        'checksum': True,
        'regexp': re.compile(r'^(?P<initial>[A-Z]{4})'
                             r'(?P<yy>\d{2})(?P<mm>\d{2})(?P<dd>\d{2})'
                             r'(?P<gender>[HMX])'
                             r'(?P<location>[A-Z]{2})'
                             r'(?P<consonant>[A-Z]{3})'
                             r'(?P<sn>[0-9A-Z])'
                             r'(?P<checksum>\d)$')
    })

    ID_CHARS = '0123456789ABCDEFGHIJKLMNÑOPQRSTUVWXYZ'
    """chars index for checksum"""
    GENDER_MAP = {
        'H': Gender.MALE,
        'M': Gender.FEMALE,
        'X': Gender.NON_BINARY
    }
    """code to gender map"""

    ALLOW_LOCATIONS = ['AS', 'BC', 'BS', 'CC', 'CH', 'CL',
                       'CM', 'CS', 'DF', 'DG', 'GR', 'GT',
                       'HG', 'JC', 'MC', 'MN', 'MS', 'NE',
                       'NL', 'NT', 'OC', 'PL', 'QR', 'QT',
                       'SL', 'SP', 'SR', 'TC', 'TL', 'TS',
                       'VZ', 'YN', 'ZS']
    """possible registration location"""

    @staticmethod
    def validate(id_number: str) -> bool:
        """validate CURP"""
        if not validate_regexp(id_number, CURP.METADATA.regexp):
            return False
        return CURP.parse(id_number) is not None

    @staticmethod
    def parse(id_number: str) -> Optional[ParseResult]:
        """parse the result"""
        match_obj = CURP.METADATA.regexp.match(id_number)
        if not match_obj:
            return None
        location = match_obj.group('location')
        checksum = CURP.checksum(id_number)
        if not checksum:
            return None
        elif location not in CURP.ALLOW_LOCATIONS:
            return None

        yy = int(match_obj.group('yy'))
        mm = int(match_obj.group('mm'))
        dd = int(match_obj.group('dd'))
        sn = match_obj.group('sn')
        year_base = 1900 if ord(sn) < 65 else 2000
        gender = match_obj.group('gender')
        try:
            return {
                'name_initial_chars': match_obj.group('initial'),
                'name_consonants': match_obj.group('consonant'),
                'yyyymmdd': date(yy + year_base, mm, dd),
                'gender': CURP.GENDER_MAP[gender],
                'location': match_obj.group('location'),
                'sn': sn,
                'checksum': int(match_obj.group('checksum'))
            }
        except ValueError:
            return None

    @staticmethod
    def checksum(id_number) -> bool:
        """check the checksum"""
        if not validate_regexp(id_number, CURP.METADATA.regexp):
            return False
        check = sum(CURP.ID_CHARS.index(c) * (18 - i) for i, c in enumerate(id_number[:17]))
        return int(id_number[17]) == (10 - check % 10) % 10


NationalID = CURP
"""alias of CURP"""
