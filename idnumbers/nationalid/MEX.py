import re
from datetime import date
from types import SimpleNamespace
from typing import Literal, Optional, TypedDict
from .util import validate_regexp
from .constant import Gender


class ParseResult(TypedDict):
    name_initial_chars: str
    name_consonants: str
    yyyymmdd: date
    gender: Gender
    location: str
    sn: str
    checksum: Literal[0, 1, 2, 3, 4, 5, 6, 7, 8, 9]


class NationalID:
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
    GENDER_MAP = {
        'H': Gender.MALE,
        'M': Gender.FEMALE,
        'X': Gender.NON_BINARY
    }

    ALLOW_LOCATIONS = ['AS', 'BC', 'BS', 'CC', 'CH', 'CL',
                       'CM', 'CS', 'DF', 'DG', 'GR', 'GT',
                       'HG', 'JC', 'MC', 'MN', 'MS', 'NE',
                       'NL', 'NT', 'OC', 'PL', 'QR', 'QT',
                       'SL', 'SP', 'SR', 'TC', 'TL', 'TS',
                       'VZ', 'YN', 'ZS']

    @staticmethod
    def validate(id_number: str) -> bool:
        if not validate_regexp(id_number, NationalID.METADATA.regexp):
            return False
        return NationalID.parse(id_number) is not None

    @staticmethod
    def parse(id_number: str) -> Optional[ParseResult]:
        match_obj = NationalID.METADATA.regexp.match(id_number)
        if not match_obj:
            return None
        location = match_obj.group('location')
        checksum = NationalID.checksum(id_number)
        if not checksum:
            return None
        elif location not in NationalID.ALLOW_LOCATIONS:
            return None
        else:
            yy = int(match_obj.group('yy'))
            mm = int(match_obj.group('mm'))
            dd = int(match_obj.group('dd'))
            sn = match_obj.group('sn')
            year_base = 1900 if ord(sn) < 65 else 2000
            gender = match_obj.group('gender')
            return {
                'name_initial_chars': match_obj.group('initial'),
                'name_consonants': match_obj.group('consonant'),
                'yyyymmdd': date(yy + year_base, mm, dd),
                'gender': NationalID.GENDER_MAP[gender],
                'location': match_obj.group('location'),
                'sn': sn,
                'checksum': int(match_obj.group('checksum'))
            }

    @staticmethod
    def checksum(id_number) -> bool:
        if not validate_regexp(id_number, NationalID.METADATA.regexp):
            return False
        check = sum(NationalID.ID_CHARS.index(c) * (18 - i) for i, c in enumerate(id_number[:17]))
        return int(id_number[17]) == (10 - check % 10) % 10


CURP = NationalID
