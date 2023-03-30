import re
from types import SimpleNamespace
from ..util import validate_regexp


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
                             r')$'),
        'alias_of': None,
        'names': ['National Health Index Number',
                  'NHI'],
        'links': ['https://techdocs.broadcom.com/us/en/symantec-security-software/information-security/'
                  'data-loss-prevention/15-8/about-data-loss-prevention-policies-v27576413-d327e9/'
                  'library-of-system-data-identifiers-v95989112-d327e56315/'
                  'new-zealand-national-health-index-number-v117807810-d327e90250/'
                  'new-zealand-national-health-index-number-narrow-br-v117808786-d327e90350.html'],
        'deprecated': False
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
