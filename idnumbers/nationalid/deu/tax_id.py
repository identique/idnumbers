import re
from collections import Counter
from ..metadata import IdMetadata
from typing import List
from ..util import CHECK_DIGIT, mn_modulus_digit, modulus_overflow_mod10, validate_regexp


def normalize(id_number: str) -> str:
    """strip out useless characters/whitespaces"""
    return re.sub(r' ', '', id_number)


class TaxID:
    """
    Germany Tax ID, Steuerliche Identifikationsnummer, Persönliche Identificationsnummer, Identifikationsnummer,
    Steuer-IdNr., IdNr or Steuer-ID.
    https://allaboutberlin.com/guides/german-tax-id-steuernummer
    python version of https://github.com/kontist/validate-steuerid

    The digit rules follow section 2.2 of the ELSTER document "Prüfung der Steuer- und Steueridentifikationsnummer"
    (Bayerisches Landesamt für Steuern):
    https://download.elster.de/download/schnittstellen/Pruefung_der_Steuer_und_Steueridentifikatsnummer.pdf

    - The first digit is not 0. Numbers with a leading 0 are test IdNrs, not real IDs, and are rejected.
    - Among the first 10 digits exactly one digit occurs two or three times, every other digit at most once.
    - A digit that occurs three times in the first 10 digits never fills three directly consecutive positions.
    - The 11th digit is the check digit.
    """
    METADATA = IdMetadata(**{
        'iso3166_alpha2': 'DE',
        'min_length': 11,
        'max_length': 11,
        'parsable': False,
        'checksum': True,
        'regexp': re.compile(r'^[1-9]\d ?\d{3} ?\d{3} ?\d{3}$'),
        'alias_of': None,
        'names': ['Tax ID',
                  'Steuerliche Identifikationsnummer',
                  'Persönliche Identificationsnummer',
                  'Identifikationsnummer',
                  'Steuer-IdNr.',
                  'IdNr',
                  'Steuer-ID'],
        'links': ['https://allaboutberlin.com/guides/german-tax-id-steuernummer',
                  'https://download.elster.de/download/schnittstellen/Pruefung_der_Steuer_und_Steueridentifikatsnummer.pdf'],
        'deprecated': False
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
        Among the first 10 digits (the check digit is excluded), exactly one digit must occur two or three times and
        every other digit at most once.
        """
        counts = Counter(normalize(id_number)[:10])
        repeated = [count for count in counts.values() if count > 1]
        return len(repeated) == 1 and repeated[0] in (2, 3)

    @staticmethod
    def check_consecutive_position(id_number: str) -> bool:
        """
        Within the first 10 digits (the check digit is excluded), no digit may fill three directly consecutive
        positions. Two adjacent equal digits are allowed.
        """
        digits = normalize(id_number)[:10]
        for index in range(len(digits) - 2):
            if digits[index] == digits[index + 1] == digits[index + 2]:
                return False
        return True
