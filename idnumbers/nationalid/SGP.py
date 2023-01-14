import re
from types import SimpleNamespace
from .util import weighted_modulus_digit, validate_regexp


class NationalID:
    """
    SGP National ID number format, UIN, FIN
    https://en.wikipedia.org/wiki/National_identification_number#Singapore
    https://www.ngiam.net/NRIC/NRIC_numbers.pdf
    python version of https://github.com/IonBazan/NRIC
    """
    METADATA = SimpleNamespace(**{
        'iso3166_alpha2': 'SG',
        'min_length': 9,
        'max_length': 9,
        'parsable': False,
        'checksum': True,
        'regexp': re.compile(r'^(?P<type>[STFGM])'
                             r'(?P<sn>\d{7})'
                             r'(?P<checksum>[A-Z])$')
    })

    MAGIC_MULTIPLIER = [2, 7, 6, 5, 4, 3, 2]
    CHECKSUM_MAP = {
        'S': 'JZIHGFEDCBA',
        'T': 'GFEDCBAJZIH',
        'F': 'XWUTRQPNMLK',
        'G': 'RQPNMLKXWUT',
        'M': 'XWUTRQPNJLK'
    }

    @staticmethod
    def validate(id_number: str) -> bool:
        """
        Validate the SGP id number
        """
        if not validate_regexp(id_number, NationalID.METADATA.regexp):
            return False
        return NationalID.checksum(id_number)

    @staticmethod
    def checksum(id_number) -> bool:
        """
        algorithm from:
        https://www.ngiam.net/NRIC/NRIC_numbers.pdf
        https://github.com/IonBazan/NRIC
        """
        if not validate_regexp(id_number, NationalID.METADATA.regexp):
            return False
        series = id_number[0]
        checksum = id_number[-1]
        # it uses modulus 11 algorithm with magic numbers
        numbers = [int(char) for char in id_number[1:-1]]
        modulus = weighted_modulus_digit(numbers, NationalID.MAGIC_MULTIPLIER, 11, True)
        return checksum == NationalID.CHECKSUM_MAP[series][modulus]
