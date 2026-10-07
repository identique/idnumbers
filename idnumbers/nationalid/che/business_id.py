import re
from ..metadata import IdMetadata
from ..util import validate_regexp

WEIGHTS = (5, 4, 3, 2, 7, 6, 5, 4)
"""the weights of the first 8 digits of the UID, the 9th digit is the check digit"""


def normalize(id_number: str) -> str:
    """strip out the insignificant characters: the dashes and dots"""
    return re.sub(r'[-.]', '', id_number)


class BusinessID:
    """
    Switzerland business identification number (UID)
    https://www.bfs.admin.ch/bfs/en/home/registers/enterprise-register/enterprise-identification/uid-general.html

    The format is CHE-123.456.789, the dashes and dots are optional. The last digit is a modulus 11 check digit:
    the first 8 digits are weighted 5, 4, 3, 2, 7, 6, 5, 4, and the check digit is 11 minus the remainder of the
    weighted sum divided by 11 (0 when the remainder is 0). A result of 10 has no single-digit check digit, so
    such a number is never valid. This follows python-stdnum (stdnum/ch/uid.py, ``calc_check_digit``).
    """
    METADATA = IdMetadata(**{
        'iso3166_alpha2': 'CH',
        # length without insignificant chars: 'CHE' and 9 digits, the optional '-' and '.' do not count
        'min_length': 12,
        'max_length': 12,
        'parsable': False,
        'checksum': True,
        'regexp': re.compile(r'^CHE-?\d{3}\.?\d{3}\.?\d{3}$'),
        'alias_of': None,
        'names': ['business identification number',
                  'UID'],
        'links': [
            'https://www.bfs.admin.ch/bfs/en/home/registers/enterprise-register/'
            'enterprise-identification/uid-general.html',
            'https://github.com/arthurdejong/python-stdnum/blob/master/stdnum/ch/uid.py'
        ],
        'deprecated': False,
        'country_name': 'Switzerland',
        'id_type': 'Business Identification Number',
        'official_name': 'Unternehmens-Identifikationsnummer',
        'display_format': 'CHE-###.###.###',
        'example': 'CHE-123.456.788',
        'checksum_algorithm': 'Weighted sum mod 11 (weights 5, 4, 3, 2, 7, 6, 5, 4; check = 11 - remainder, a result '
                              'of 10 is invalid)',
        'masks': ('LLL-###.###.###', 'LLL#########')
    })

    @staticmethod
    def validate(id_number: str) -> bool:
        """validate the number"""
        return BusinessID.checksum(id_number)

    @staticmethod
    def checksum(id_number: str) -> bool:
        """check the format, then the modulus 11 check digit"""
        if not validate_regexp(id_number, BusinessID.METADATA.regexp):
            return False
        # the regexp leaves 'CHE' and 9 ASCII digits once the dashes and dots are stripped
        digits = [int(char) for char in normalize(id_number)[3:]]
        total = sum(weight * digit for weight, digit in zip(WEIGHTS, digits))
        # a result of 10 is never equal to a single digit: such a number is invalid
        return digits[8] == (11 - total) % 11
