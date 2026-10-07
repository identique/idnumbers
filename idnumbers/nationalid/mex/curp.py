import re
from datetime import date
from ..metadata import IdMetadata
from typing import Literal, Optional, TypedDict, cast
from ..constant import Gender
from ..util import CHECK_DIGIT, validate_regexp, match_regexp


# RENAPO's March 2006 Instructivo Normativo, Annex 2 (printed page 59), lists these
# original inconvenient prefixes; page 7 requires replacing their second letter with X.
_INCONVENIENT_PREFIXES = frozenset({
    'BACA', 'BAKA', 'BUEI', 'BUEY', 'CACA', 'CACO', 'CAGA', 'CAGO', 'CAKA',
    'CAKO', 'COGE', 'COGI', 'COJA', 'COJE', 'COJI', 'COJO', 'COLA', 'CULO',
    'FALO', 'FETO', 'GETA', 'GUEI', 'GUEY', 'JETA', 'JOTO', 'KACA', 'KACO',
    'KAGA', 'KAGO', 'KAKA', 'KAKO', 'KOGE', 'KOGI', 'KOJA', 'KOJE', 'KOJI',
    'KOJO', 'KOLA', 'KULO', 'LILO', 'LOCA', 'LOCO', 'LOKA', 'LOKO', 'MAME',
    'MAMO', 'MEAR', 'MEAS', 'MEON', 'MIAR', 'MION', 'MOCO', 'MOKO', 'MULA',
    'MULO', 'NACA', 'NACO', 'PEDA', 'PEDO', 'PENE', 'PIPI', 'PITO', 'POPO',
    'PUTA', 'PUTO', 'QULO', 'RATA', 'ROBA', 'ROBE', 'ROBO', 'RUIN', 'SENO',
    'TETA', 'VACA', 'VAGA', 'VAGO', 'VAKA', 'VUEI', 'VUEY', 'WUEI', 'WUEY',
})


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
    RENAPO, Instructivo Normativo (March 2006), printed pages 7 and 59:
    https://ordenjuridico.gob.mx/Federal/PE/APF/APC/SEGOB/Instructivos/InstructivoNormativo.pdf
    python version of https://github.com/d3249/curp
    """
    METADATA = IdMetadata(**{
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
                             r'(?P<checksum>\d)$'),
        'alias_of': None,
        'names': ['CURP',
                  'Clave Única de Registro de Población',
                  'Unique Population Registry Code',
                  'Personal ID Code Number'],
        'links': ['https://en.wikipedia.org/wiki/Unique_Population_Registry_Code',
                  'https://ordenjuridico.gob.mx/Federal/PE/APF/APC/SEGOB/Instructivos/InstructivoNormativo.pdf'],
        'deprecated': False,
        'country_name': 'Mexico',
        'id_type': 'Unique Population Registry Code',
        'official_name': 'Clave Única de Registro de Población',
        'display_format': 'AAAANNNNNNAAAAAANN',
        'example': 'HEGG560427MVZRRL04',
        'checksum_algorithm': 'Weighted sum mod 10 (positions weighted 18-2 over the alphabet 0-9, A-N, Ñ, O-Z; check '
                              '= (10 - remainder) mod 10)',
        'masks': ('LLLL######LLLLLLX#',)
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
        match_obj = match_regexp(id_number, CURP.METADATA.regexp)
        if not match_obj:
            return None
        if match_obj.group('initial') in _INCONVENIENT_PREFIXES:
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
                'checksum': cast(CHECK_DIGIT, int(match_obj.group('checksum')))
            }
        except ValueError:
            return None

    @staticmethod
    def checksum(id_number: str) -> bool:
        """check the checksum"""
        if not validate_regexp(id_number, CURP.METADATA.regexp):
            return False
        check = sum(CURP.ID_CHARS.index(c) * (18 - i) for i, c in enumerate(id_number[:17]))
        return int(id_number[17]) == (10 - check % 10) % 10
