import re
from types import SimpleNamespace
from ..util import validate_regexp, ean13_digit


def normalize(id_number: str) -> str:
    """strip out useless characters/whitespaces"""
    return re.sub(r'\.', '', id_number)


class SocialSecurityNumber:
    """
    Switzerland Social Security Number (AHV-Nr. [de] / No AVS [fr])
    https://en.wikipedia.org/wiki/National_identification_number#Switzerland
    """
    METADATA = SimpleNamespace(**{
        'iso3166_alpha2': 'CH',
        # length without insignificant chars
        'min_length': 13,
        'max_length': 13,
        'parsable': False,
        'checksum': True,
        'regexp': re.compile(r'^756\.\d{4}\.\d{4}.\d{2}$'),
        'alias_of': None,
        'names': ['Social Security Number',
                  'AHV-Nr.',
                  'No AVS'],
        'links': ['https://en.wikipedia.org/wiki/National_identification_number#Switzerland'],
        'deprecated': False

    })

    @staticmethod
    def validate(id_number: str) -> bool:
        """validate the number"""
        return SocialSecurityNumber.checksum(id_number)

    @staticmethod
    def checksum(id_number: str) -> bool:
        """use EAN-13 to validate the number"""
        if not validate_regexp(id_number, SocialSecurityNumber.METADATA.regexp):
            return False
        numbers = [int(char) for char in normalize(id_number)]
        return numbers[-1] == ean13_digit(numbers[:-1])
