import re
from types import SimpleNamespace
from typing import Optional
from .util import CHECK_DIGIT, validate_regexp


def normalize(id_number):
    """strip out useless characters/whitespaces"""
    return re.sub(r'[ \-/]', '', id_number)


class TaxFileNumber:
    """
    Australia tax file number format
    Note: Australian law specifically prohibits the use of the TFN as a national identification number
    https://en.wikipedia.org/wiki/National_identification_number#Australia
    https://en.wikipedia.org/wiki/Tax_file_number
    https://www.ato.gov.au/General/What-is-a-tax-file-number----Easy-Read/
    https://en-academic.com/dic.nsf/enwiki/436130
    """
    METADATA = SimpleNamespace(**{
        'iso3166_alpha2': 'AU',
        # length without insignificant chars
        'min_length': 8,
        'max_length': 9,
        # has parse function
        'parsable': False,
        # has checksum function
        'checksum': True,
        # regular expression to validate the id
        'regexp': re.compile(r'^(\d{9}|\d{8})$')
    })

    MAGIC_MULTIPLIER = [1, 4, 3, 7, 5, 8, 6, 9, 10]
    """The magic multiplier for checksum"""

    @staticmethod
    def validate(id_number: str) -> bool:
        """
        Validate the AUS tax file number
        """
        if not validate_regexp(id_number, TaxFileNumber.METADATA.regexp):
            return False
        return TaxFileNumber.checksum(id_number) == 0

    @staticmethod
    def checksum(id_number: str) -> Optional[int]:
        if not validate_regexp(id_number, TaxFileNumber.METADATA.regexp):
            return None
        """algorithm: https://en.wikipedia.org/wiki/Tax_file_number#Check_digit"""
        normalized = normalize(id_number)
        if len(normalized) == 8:
            normalized = normalized[0:7] + '0' + normalized[7]
        number_list = [int(char) for char in list(normalized)]
        return sum([value * TaxFileNumber.MAGIC_MULTIPLIER[index] for (index, value) in enumerate(number_list)]) % 11


class DriverLicenseNumber:
    """
    Australia driver license number format
    https://learn.microsoft.com/en-us/microsoft-365/compliance/sit-defn-australia-drivers-license-number?view=o365-worldwide
    https://techdocs.broadcom.com/us/en/symantec-security-software/information-security/data-loss-prevention/15-8/about-data-loss-prevention-policies-v27576413-d327e9/library-of-system-data-identifiers-v95989112-d327e56315/australia-driver-s-license-number-v130004514-d327e56830.html
    """
    METADATA = SimpleNamespace(**{
        'iso3166_alpha2': 'AU',
        # length without insignificant chars
        'min_length': 6,
        'max_length': 10,
        # has parse function
        'parsable': False,
        # has checksum function
        'checksum': False,
        # regular expression to validate the id
        'regexp': re.compile(r'^('
                             r'\d{9}|\d{3} \d{3} \d{3}|'
                             r'\d{8}|\d{2} \d{3} \d{3}|'
                             r'[A-Za-z]\d{5}|'
                             r'\d{10}|\d{3}-\d{3}-\d{4}'
                             r')$')
    })

    BLACK_TRAILING_NUMBER = ['00000', '11111', '22222', '33333', '44444', '55555', '66666', '77777', '88888', '99999']
    """black list for some numbers"""

    @staticmethod
    def validate(id_number: str) -> bool:
        """
        Validate the AUS driver license number
        """
        if not validate_regexp(id_number, DriverLicenseNumber.METADATA.regexp):
            return False
        return normalize(id_number)[-5:] not in DriverLicenseNumber.BLACK_TRAILING_NUMBER


class MedicareNumber:
    """
    Australia medicare number format
    https://techdocs.broadcom.com/us/en/symantec-security-software/information-security/data-loss-prevention/15-8/about-data-loss-prevention-policies-v27576413-d327e9/library-of-system-data-identifiers-v95989112-d327e56315/australian-medicare-number-v115447646-d327e57399.html
    """
    METADATA = SimpleNamespace(**{
        'iso3166_alpha2': 'AU',
        # length without insignificant chars
        'min_length': 9,
        'max_length': 11,
        # has parse function
        'parsable': False,
        # has checksum function
        'checksum': True,
        # regular expression to validate the id
        'regexp': re.compile(r'^('
                             r'[2-6]\d{10}|[2-6]\d{3} \d{5} \d|[2-6]\d{3}-\d{5}-\d|'
                             r'[2-6]\d{9}|[2-6]\d{9}([-/]\d)?|'
                             r'[2-6]\d{3} \d{5} \d([-/]\d)?|[2-6]\d{3}-\d{5}-\d([-/]\d)?|'
                             r'[2-6]\d{3} \d{5} \d \d|[2-6]\d{3}-\d{5}-\d-\d'
                             r')$')
    })

    MAGIC_MULTIPLIER = [1, 3, 7, 9, 1, 3, 7, 9]
    """magic multiplier for checksum"""

    @staticmethod
    def validate(id_number: str) -> bool:
        """
        Validate the medicare number
        """
        if not validate_regexp(id_number, MedicareNumber.METADATA.regexp):
            return False
        normalized = normalize(id_number)
        checksum = MedicareNumber.checksum(id_number)
        return checksum is not None and checksum == int(normalized[8])

    @staticmethod
    def checksum(id_number: str) -> Optional[CHECK_DIGIT]:
        if not validate_regexp(id_number, MedicareNumber.METADATA.regexp):
            return None
        """algorithm: https://stackoverflow.com/questions/3589345/how-do-i-validate-an-australian-medicare-number."""
        normalized = normalize(id_number)
        # only validate first 8 digits
        number_list = [int(char) for char in list(normalized)][:8]
        total = sum([value * MedicareNumber.MAGIC_MULTIPLIER[index] for (index, value) in enumerate(number_list)])
        return total % 10
