import re
from enum import Enum
from types import SimpleNamespace
from typing import Literal, Optional, TypedDict
from .util import weighted_modulus_digit, modulus_overflow_mod10, validate_regexp


class ThaiCitizenship(Enum):
    # Not used for Thai nationals, occasionally on other cards
    OTHER = 0
    # Thai Nationals. Born after 1st Jan 1984
    CITIZEN_AFTER_1984 = 1
    # Thai Nationals. Born after 1st Jan 1984. Birth notified late
    CITIZEN_AFTER_1984_LATE_REGISTERED = 2
    # Thai Nationals. Born & registered before 1st Jan 1984
    CITIZEN_BEFORE_1984 = 3
    # Thai Nationals. Born before 1st Jan 1984. Registered late.
    CITIZEN_BEFORE_1984_LATE_REGISTERED = 4
    # Thai Nationals. Missed census or special cases.
    CITIZEN_SPECIAL_CASE = 5
    # Foreign Nationals living temporarily, or illegal migrants.
    FOREIGN_RESIDENT = 6
    # Children of #6 who were born in Thailand.
    FOREIGN_RESIDENT_CHILDREN = 7
    # Foreign Nationals living permanently, or Thai nationals by naturalisation.
    PERMANENT_RESIDENT = 8


def normalize(id_number):
    return re.sub(r'[ \-/]', '', id_number)


class ParseResult(TypedDict):
    citizenship: ThaiCitizenship
    province_code: str
    distinct_code: str
    sn: str
    checksum: Literal[0, 1, 2, 3, 4, 5, 6, 7, 8, 9]


class NationalID:
    """
    THA National ID number format
    https://en.wikipedia.org/wiki/National_identification_number#Thailand
    https://thailandformats.com/idcards

    This is the python version of https://github.com/awcode/thai-laravel
    """
    METADATA = SimpleNamespace(**{
        'iso3166_alpha2': 'TH',
        'min_length': 13,
        'max_length': 13,
        'parsable': True,
        'checksum': True,
        'regexp': re.compile(r'^(?P<citizenship>[0-8])[ -]?'
                             r'(?P<province>\d{2})'
                             r'(?P<distinct>\d{2})[ -]?'
                             r'(?P<sn>\d{5}[ -]?\d{2})[ -]?'
                             r'(?P<checksum>\d)$')
    })

    PROVINCE_LIST = ['10', '11', '12', '13', '14', '15', '16', '17', '18', '19',
                     '20', '21', '22', '23', '24', '25', '26', '27',
                     '30', '31', '32', '33', '34', '35', '36', '37', '38', '39',
                     '40', '41', '42', '43', '44', '45', '46', '47', '48', '49',
                     '50', '51', '52', '53', '54', '55', '56', '57', '58',
                     '60', '61', '62', '63', '64', '65', '66', '67',
                     '70', '71', '72', '73', '74', '75', '76', '77',
                     '80', '81', '82', '83', '84', '85', '86',
                     '90', '91', '92', '93', '94', '95', '96']
    DISTINCT_MAX_VALUE = {
        '10': 50, '11': 6, '12': 6, '13': 7, '14': 46, '15': 7, '16': 11, '17': 9, '18': 8, '19': 12,
        '20': 11, '21': 8, '22': 10, '23': 7, '24': 11, '25': 9, '26': 4, '27': 9,
        '30': 32, '31': 23, '32': 17, '33': 22, '34': 25, '35': 9, '36': 16, '37': 6, '38': 8, '39': 6,
        '40': 26, '41': 25, '42': 14, '43': 9, '44': 13, '45': 20, '46': 18, '47': 18, '48': 12, '49': 7,
        '50': 25, '51': 8, '52': 12, '53': 9, '54': 16, '55': 15, '56': 9, '57': 18, '58': 7,
        '60': 15, '61': 8, '62': 11, '63': 9, '64': 9, '65': 22, '66': 13, '67': 13,
        '70': 10, '71': 13, '72': 10, '73': 7, '74': 3, '75': 3, '76': 7, '77': 8,
        '80': 23, '81': 8, '82': 8, '83': 3, '84': 19, '85': 4, '86': 8,
        '90': 16, '91': 7, '92': 10, '93': 11, '94': 11, '95': 8, '96': 13,
    }
    DISTINCT_SPECIAL_CASE = {'44': [95]}

    MAGIC_MULTIPLIER = [13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2]

    @staticmethod
    def validate(id_number: str) -> bool:
        """
        Validate the THA id number
        """
        if not validate_regexp(id_number, NationalID.METADATA.regexp):
            return False
        return NationalID.parse(id_number) is not None

    @staticmethod
    def parse(id_number: str) -> Optional[ParseResult]:
        match_obj = NationalID.METADATA.regexp.match(id_number)
        if not match_obj:
            return None
        citizenship = match_obj.group('citizenship')
        province = match_obj.group('province')
        distinct = match_obj.group('distinct')
        sn = normalize(match_obj.group('sn'))
        checksum = NationalID.checksum(id_number)
        if not NationalID.check_province_code(province):
            return None
        if not NationalID.check_distinct_code(province, distinct):
            return None
        if not checksum:
            return None
        else:
            return {
                'citizenship': ThaiCitizenship(int(citizenship)),
                'province_code': province,
                'distinct_code': distinct,
                'sn': sn,
                'checksum': int(match_obj.group('checksum'))
            }

    @staticmethod
    def checksum(id_number) -> bool:
        if not validate_regexp(id_number, NationalID.METADATA.regexp):
            return False
        # it uses modulus 11 algorithm with magic numbers
        numbers = [int(char) for char in normalize(id_number)]
        modulus = modulus_overflow_mod10(weighted_modulus_digit(numbers[:-1], NationalID.MAGIC_MULTIPLIER, 11))
        return modulus == numbers[-1]

    @staticmethod
    def check_province_code(province_code: str) -> bool:
        return province_code in NationalID.PROVINCE_LIST

    @staticmethod
    def check_distinct_code(province_code: str, distinct_code: str) -> bool:
        if distinct_code == '99':
            return True
        distinct_int = int(distinct_code)
        if distinct_int <= NationalID.DISTINCT_MAX_VALUE[province_code]:
            return True
        if province_code not in NationalID.DISTINCT_SPECIAL_CASE:
            return False
        return distinct_int in NationalID.DISTINCT_SPECIAL_CASE[province_code]
