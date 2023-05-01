import math
import re
from types import SimpleNamespace
from ..util import validate_regexp, weighted_modulus_digit, modulus_overflow_mod10


def normalize(id_number: str) -> str:
    return re.sub(r'/', '', id_number)


class TaxNumber:
    """
    Czech Republic tax number format
    https://gist.github.com/svschannak/e79892f4fbc56df15bdb5496d0e67b85

    """
    METADATA = SimpleNamespace(**{
        'iso3166_alpha2': 'CZ',
        'min_length': 8,
        'max_length': 10,
        'parsable': False,
        'checksum': True,
        'regexp': re.compile(r'^\d{8,10}$'),
        'alias_of': None,
        'names': ['tax number',
                  'daňové identifikační číslo',
                  'DIČ',
                  'VAT identification number'],
        'links': ['https://tincheck.io/czech-republic/',
                  'https://www.oecd.org/tax/automatic-exchange/crs-implementation-and-assistance/'
                  'tax-identification-numbers/CZ-TIN.pdf',
                  'https://gist.github.com/svschannak/e79892f4fbc56df15bdb5496d0e67b85'],
        'deprecated': False
    })

    MULTIPLIER = [8, 7, 6, 5, 4, 3, 2]
    CHECK_MAP = [8, 7, 6, 5, 4, 3, 2, 1, 0, 9, 8]

    @staticmethod
    def validate(id_number: str) -> bool:
        return TaxNumber.checksum(id_number)

    @staticmethod
    def checksum(id_number: str) -> bool:
        """
        src: https://gist.github.com/svschannak/e79892f4fbc56df15bdb5496d0e67b85
        """
        normalized = normalize(id_number)
        if not validate_regexp(normalized, TaxNumber.METADATA.regexp):
            return False
        elif not TaxNumber.is_individual(normalized):
            return TaxNumber.checksum_entity(normalized)
        elif len(normalized) == 9:
            if int(normalized[0]) < 6:
                # no checksum
                return True
            else:
                return TaxNumber.checksum_old_individual(normalized)
        else:
            # no checksum
            return True

    @staticmethod
    def checksum_entity(id_number: str) -> bool:
        numbers = [int(char) for char in id_number[:-1]]
        modulus = modulus_overflow_mod10(weighted_modulus_digit(numbers, TaxNumber.MULTIPLIER, 11))
        return str(modulus) == id_number[-1]

    @staticmethod
    def checksum_old_individual(id_number: str) -> bool:
        numbers = [int(char) for char in id_number[1:-1]]
        total = sum([value * TaxNumber.MULTIPLIER[index] for (index, value) in enumerate(numbers)])
        check_digit = 10 if total % 11 == 0 else math.ceil(total / 11) * 11 - total - 1

        return str(TaxNumber.CHECK_MAP[check_digit]) == id_number[-1]

    @staticmethod
    def is_individual(id_number: str) -> bool:
        length = len(normalize(id_number))
        return length == 9 or length == 10
