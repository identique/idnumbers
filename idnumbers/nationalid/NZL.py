import re
from types import SimpleNamespace
from typing import List
from .util import validate_regexp


def normalize(id_number):
    """strip out useless characters/whitespaces"""
    return re.sub(r'-', '', id_number)


BLACK_TRAILING_NUMBER = ['000000', '111111', '222222', '333333', '444444', '555555', '666666', '777777', '888888',
                         '999999']
"""blacklist for the trailing numbers"""


class DriverLicenseNumber:
    """
    New Zealand driver license number format
    https://techdocs.broadcom.com/us/en/symantec-security-software/information-security/data-loss-prevention/15-8/about-data-loss-prevention-policies-v27576413-d327e9/library-of-system-data-identifiers-v95989112-d327e56315/new-zealand-driver-s-licence-number-v130004625-d327e90104/new-zealand-driver-s-licence-number-narrow-breadth-v130007408-d327e90179.html#v130007408
    """
    METADATA = SimpleNamespace(**{
        'iso3166_alpha2': 'NZ',
        # length without insignificant chars
        'min_length': 8,
        'max_length': 8,
        # has parse function
        'parsable': False,
        # has checksum function
        'checksum': False,
        # regular expression to validate the id
        'regexp': re.compile(r'^\w{2}\d{6}$')
    })

    @staticmethod
    def validate(id_number: str) -> bool:
        """
        Validate the NZL driver license number
        """
        if not validate_regexp(id_number, DriverLicenseNumber.METADATA.regexp):
            return False
        return id_number[-6:] not in BLACK_TRAILING_NUMBER


class PassportNumber:
    """
    New Zealand passport number format
    https://techdocs.broadcom.com/us/en/symantec-security-software/information-security/data-loss-prevention/15-8/about-data-loss-prevention-policies-v27576413-d327e9/library-of-system-data-identifiers-v95989112-d327e56315/new-zealand-passport-number-v130004628-d327e90423/new-zealand-passport-number-narrow-breadth-v130007458-d327e90528.html
    """
    METADATA = SimpleNamespace(**{
        'iso3166_alpha2': 'NZ',
        # length without insignificant chars
        'min_length': 7,
        'max_length': 8,
        # has parse function
        'parsable': False,
        # has checksum function
        'checksum': False,
        # regular expression to validate the id
        'regexp': re.compile(r'^([Ll][Aa]|[Ll][Dd]|[Ll][Ff]|[Nn]|[Ee][Aa]|[Ll][Hh])\d{6}$')
    })

    @staticmethod
    def validate(id_number: str) -> bool:
        """
        Validate the NZL passport number
        """
        if not validate_regexp(id_number, PassportNumber.METADATA.regexp):
            return False
        return id_number[-6:] not in BLACK_TRAILING_NUMBER


class InlandRevenueDepartmentNumber:
    """
    New Zealand inland revenue department(IRD) number format
    https://www.oecd.org/tax/automatic-exchange/crs-implementation-and-assistance/tax-identification-numbers/New%20Zealand-TIN.pdf
    This is a python version of this one: https://github.com/jarden-digital/nz-ird-validator
    """
    METADATA = SimpleNamespace(**{
        'iso3166_alpha2': 'NZ',
        # length without insignificant chars
        'min_length': 8,
        'max_length': 9,
        # has parse function
        'parsable': False,
        # has checksum function
        'checksum': True,
        # regular expression to validate the id
        'regexp': re.compile(r'^('
                             r'\d{9}|\d{3}-\d{3}-\d{3}|'
                             r'\d{8}|\d{2}-\d{3}-\d{3}'
                             r')$')
    })

    PHASE1_MULTIPLIER = [3, 2, 7, 6, 5, 4, 3, 2]
    PHASE2_MULTIPLIER = [7, 4, 3, 2, 5, 2, 7, 6]

    @staticmethod
    def validate(id_number: str) -> bool:
        """
        Validate the NZL IRD number
        """
        return InlandRevenueDepartmentNumber.checksum(id_number)

    @staticmethod
    def checksum(id_number: str) -> bool:
        """algorithm: https://github.com/jarden-digital/nz-ird-validator"""
        if not validate_regexp(id_number, InlandRevenueDepartmentNumber.METADATA.regexp):
            return False
        normalized = normalize(id_number)
        if len(normalized) == 8:
            # pre-pad a 0 if it is the short one
            normalized = '0' + normalized
        number_list = [int(char) for char in list(normalized)]
        # split to source list and check digit
        source_list = number_list[:8]
        check_digit = number_list[8]
        # phase 1
        calculated = InlandRevenueDepartmentNumber.calc_checkdigit(source_list,
                                                                   InlandRevenueDepartmentNumber.PHASE1_MULTIPLIER)
        if calculated != 10:
            return calculated == check_digit
        # phase 2
        calculated2 = InlandRevenueDepartmentNumber.calc_checkdigit(source_list,
                                                                    InlandRevenueDepartmentNumber.PHASE2_MULTIPLIER)
        return (calculated2 == check_digit) if calculated2 < 10 else False

    @staticmethod
    def calc_checkdigit(source_list: List[int], magic_numbers: List[int]) -> int:
        modulus = sum([value * magic_numbers[index] for (index, value) in enumerate(source_list)]) % 11
        return 0 if modulus == 0 else (11 - modulus)


class NationalHealthIndexNumber:
    """
    New Zealand national health index(NHI) number format
    https://techdocs.broadcom.com/us/en/symantec-security-software/information-security/data-loss-prevention/15-8/about-data-loss-prevention-policies-v27576413-d327e9/library-of-system-data-identifiers-v95989112-d327e56315/new-zealand-national-health-index-number-v117807810-d327e90250/new-zealand-national-health-index-number-narrow-br-v117808786-d327e90350.html
    This is a python version of this one: https://gist.github.com/mcshaz/b41dc6bd4aa3104d54da677e2b4f6b45
    """
    METADATA = SimpleNamespace(**{
        'iso3166_alpha2': 'NZ',
        # length without insignificant chars
        'min_length': 7,
        'max_length': 7,
        # has parse function
        'parsable': False,
        # has checksum function
        'checksum': True,
        # regular expression to validate the id
        # no I and no O in alphabet
        'regexp': re.compile(r'^('
                             r'[A-HJ-NP-Z]{3}\d{4}|'
                             r'[A-HJ-NP-Z]{3}\d{2}[A-HJ-NP-Z]{2}|'
                             r')$')
    })

    ALPHABET_LIST = list('ABCDEFGHJKLMNPQRSTUVWXYZ')

    @staticmethod
    def validate(id_number: str) -> bool:
        """
        Validate the NZL NHI number
        """
        return NationalHealthIndexNumber.checksum(id_number)

    @staticmethod
    def checksum(id_number: str) -> bool:
        """algorithm: https://gist.github.com/mcshaz/b41dc6bd4aa3104d54da677e2b4f6b45"""
        if not validate_regexp(id_number, NationalHealthIndexNumber.METADATA.regexp):
            return False
        check_digit = id_number[-1]
        source_list = list(id_number[:-1])
        total = 0
        for (index, char) in enumerate(source_list):
            if char in NationalHealthIndexNumber.ALPHABET_LIST:
                decimal = NationalHealthIndexNumber.ALPHABET_LIST.index(char) + 1
            else:
                decimal = int(char)
            total += decimal * (7 - index)
        if check_digit in NationalHealthIndexNumber.ALPHABET_LIST:
            # new NHI format
            modulus = total % 24
            return NationalHealthIndexNumber.ALPHABET_LIST[23 - modulus] == check_digit
        else:
            check_decimal = int(check_digit)
            # old NHI format
            modulus = total % 11
            if modulus == 0:
                return False
            return check_decimal == 0 if modulus == 1 else check_decimal == (11 - modulus)
