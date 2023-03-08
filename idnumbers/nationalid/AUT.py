import re
from types import SimpleNamespace
from .util import validate_regexp


def normalize(id_number):
    """strip out useless characters/whitespaces"""
    return re.sub(r'[-/]', '', id_number)


class TaxIDNumber:
    """
    Austria tax id number format
    https://www.oecd.org/tax/automatic-exchange/crs-implementation-and-assistance/tax-identification-numbers/Austria-TIN.pdf
    """
    METADATA = SimpleNamespace(**{
        'iso3166_alpha2': 'AT',
        # length without insignificant chars
        'min_length': 9,
        'max_length': 9,
        # has parse function
        'parsable': False,
        # has checksum function
        'checksum': True,
        # regular expression to validate the id
        'regexp': re.compile(r'^(\d{2}-?\d{3}/?\d{4})$')
    })

    MULTIPLIER = [1, 2, 1, 2, 1, 2, 1, 2]
    """The multiplier for checksum"""
    OVERFLOW_SUM = {
        10: 1,
        12: 3,
        14: 5,
        16: 7,
        18: 9
    }
    """checksum algorithm shows we have to sum the two digits if the weighted value > 9"""

    @staticmethod
    def validate(id_number: str) -> bool:
        """
        Validate the tax id number
        """
        if not validate_regexp(id_number, TaxIDNumber.METADATA.regexp):
            return False
        return TaxIDNumber.checksum(id_number)

    @staticmethod
    def checksum(id_number: str) -> bool:
        if not validate_regexp(id_number, TaxIDNumber.METADATA.regexp):
            return False
        """algorithm: https://en.wikipedia.org/wiki/Tax_file_number#Check_digit"""
        normalized = normalize(id_number)
        numbers = [int(char) for char in list(normalized)]
        total = 0
        for (index, value) in enumerate(numbers[:-1]):
            weighted = value * TaxIDNumber.MULTIPLIER[index]
            if weighted in TaxIDNumber.OVERFLOW_SUM:
                weighted = TaxIDNumber.OVERFLOW_SUM[weighted]
            total += weighted
        checksum = (100 - total) % 10
        return checksum == numbers[-1]


NationalID = TaxIDNumber
"""alias of TaxIDNumber"""
