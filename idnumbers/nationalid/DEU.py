import re
from types import SimpleNamespace
from typing import List
from .util import CHECK_DIGIT, mn_modulus_digit, modulus_overflow_mod10, validate_regexp


def normalize(id_number):
    """strip out useless characters/whitespaces"""
    return re.sub(r' ', '', id_number)


class TaxID:
    """
    Germany Tax ID, Steuerliche Identifikationsnummer, Persönliche Identificationsnummer, Identifikationsnummer,
    Steuer-IdNr., IdNr or Steuer-ID.
    https://allaboutberlin.com/guides/german-tax-id-steuernummer
    python version of https://github.com/kontist/validate-steuerid
    """
    METADATA = SimpleNamespace(**{
        'iso3166_alpha2': 'DE',
        'min_length': 11,
        'max_length': 11,
        'parsable': False,
        'checksum': True,
        'regexp': re.compile(r'^\d{2} ?\d{3} ?\d{3} ?\d{3}$')
    })

    @staticmethod
    def validate(id_number: str) -> bool:
        """
        Validate the DEU Tax ID
        """
        if not validate_regexp(id_number, TaxID.METADATA.regexp):
            return False
        elif not TaxID.check_multiple_occurrence(id_number):
            return False
        elif not TaxID.check_consecutive_position(id_number):
            return False
        return TaxID.checksum(id_number)

    @staticmethod
    def checksum(id_number: str) -> bool:
        """check if the ID valid against its checksum"""
        if not validate_regexp(id_number, TaxID.METADATA.regexp):
            return False
        numbers = [int(char) for char in normalize(id_number)]
        check = numbers[-1]
        return int(check) == TaxID.get_checkdigit(numbers[:-1])

    @staticmethod
    def get_checkdigit(numbers: List[int]) -> CHECK_DIGIT:
        return modulus_overflow_mod10(mn_modulus_digit(numbers, 10, 11))

    @staticmethod
    def check_multiple_occurrence(id_number: str) -> bool:
        """
        We can only have 1 digit with multiple occurrence in the number
        """
        normalized = list(normalize(id_number))[:-1]
        normalized.sort()
        first_multiple_digits = None
        for index, digit in enumerate(normalized):
            if index == 0:
                continue
            if not first_multiple_digits and digit == normalized[index - 1]:
                # no first occurrence, we set the digit to the first_multiple_digits
                first_multiple_digits = digit
            elif first_multiple_digits != digit and digit == normalized[index - 1]:
                # we already saw first_multiple_digits and find it again. it's wrong
                return False
            # first_multiple_digits == digit and digit == normalized[index - 1] means the 3rd occurrence. It's ok.
        return True

    @staticmethod
    def check_consecutive_position(id_number: str) -> bool:
        """
        We can have a number with 2 consecutive position at most.
        """
        normalized = list(normalize(id_number))
        # minus one for getting rid of check digit
        for index in range(len(normalized) - 2):
            if normalized[index] == normalized[index + 1] and normalized[index] == normalized[index + 2]:
                return False
        return True


IdNr = TaxID
"""alias of TaxID"""
NationalID = TaxID
"""alias of TaxID"""

# TODO: implement TaxNumber
