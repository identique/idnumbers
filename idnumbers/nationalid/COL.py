import re
from types import SimpleNamespace
from .util import CHECK_DIGIT, validate_regexp, weighted_modulus_digit


def normalize(id_number):
    """strip out useless characters/whitespaces"""
    return re.sub(r'[-. ]', '', id_number)


def colombia_checksum(id_number: str) -> CHECK_DIGIT:
    """
    Python version of
    https://github.com/anghelvalentin/CountryValidator/blob/master/CountryValidator/CountriesValidators/ColombiaValidator.cs
    """
    numbers = [int(char) for char in list(normalize(id_number[:-1]))]
    numbers.reverse()
    modulus = weighted_modulus_digit(numbers, UniquePersonalID.WEIGHTS[0:len(numbers)], 11)
    if modulus == 11:
        return 0
    elif modulus == 10:
        return 1
    else:
        return modulus


class UniquePersonalID:
    """
    UniquePersonalID, NUIP, Número único de identidad personal
    https://en.wikipedia.org/wiki/Colombian_identity_card
    https://validatetin.com/colombia/#
    """
    METADATA = SimpleNamespace(**{
        'iso3166_alpha2': 'CO',
        # length without insignificant chars
        'min_length': 9,
        'max_length': 10,
        # has parse function
        'parsable': False,
        # has checksum function
        'checksum': True,
        # regular expression to validate the id
        'regexp': re.compile(r'^(\d{2,3}\.?\d{3}\.?\d{3}-?\d)$')
    })

    WEIGHTS = [3, 7, 13, 17, 19, 23, 29, 37, 41, 43, 47, 53, 59, 67, 71]

    @staticmethod
    def validate(id_number: str) -> bool:
        """
        Validate id number
        """
        if not validate_regexp(id_number, UniquePersonalID.METADATA.regexp):
            return False
        return UniquePersonalID.checksum(id_number) == int(id_number[-1])

    @staticmethod
    def checksum(id_number: str) -> CHECK_DIGIT:
        if not validate_regexp(id_number, UniquePersonalID.METADATA.regexp):
            return False
        return colombia_checksum(id_number)


NUIP = UniquePersonalID
"""alias of UniquePersonalID"""
