import re
from types import SimpleNamespace
from typing import List
from ..util import validate_regexp


def normalize(id_number):
    """strip out useless characters/whitespaces"""
    return re.sub(r'-', '', id_number)


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
                             r')$'),
        'alias_of': None,
        'names': ['Inland Revenue Department Number',
                  'IRD'],
        'links': ['https://www.oecd.org/tax/automatic-exchange/crs-implementation-and-assistance/'
                  'tax-identification-numbers/New%20Zealand-TIN.pdf'],
        'deprecated': False
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
