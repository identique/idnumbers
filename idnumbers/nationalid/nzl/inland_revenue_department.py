import re
from ..metadata import IdMetadata
from typing import List
from ..util import validate_regexp


def normalize(id_number: str) -> str:
    """strip out useless characters/whitespaces"""
    return re.sub(r'-', '', id_number)


class InlandRevenueDepartmentNumber:
    """
    New Zealand inland revenue department(IRD) number format
    https://www.oecd.org/tax/automatic-exchange/crs-implementation-and-assistance/tax-identification-numbers/New%20Zealand-TIN.pdf
    Range and checksum: IRD's 2026 overseas pension transfers file specification,
    section 5.3 (inclusive range 10,000,000 to 200,000,000).
    This is a python version of this one: https://github.com/jarden-digital/nz-ird-validator
    """
    METADATA = IdMetadata(**{
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
        'links': ['https://www.ird.govt.nz/-/media/project/ir/home/documents/kiwisaver/'
                  'file-upload-spec-for-opt/file-upload-specification---overseas-pension-transfers-return---2026.pdf'
                  '?modified=20260302011849',
                  'https://www.ird.govt.nz/updates/news-folder/2026/increase-to-ird-number-validation-upper-limit',
                  'https://www.oecd.org/tax/automatic-exchange/crs-implementation-and-assistance/'
                  'tax-identification-numbers/New%20Zealand-TIN.pdf'],
        'deprecated': False,
        'country_name': 'New Zealand',
        'id_type': 'Inland Revenue Department Number',
        'official_name': None,
        'display_format': '##-###-###',
        'example': '49-091-850',
        'checksum_algorithm': 'Weighted sum mod 11 in two passes (weights 3, 2, 7, 6, 5, 4, 3, 2; then 7, 4, 3, 2, 5, '
                              '2, 7, 6 when the first check digit is 10)',
        'masks': ('##-###-###', '###-###-###', '########', '#########')
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
        if not 10000000 <= int(normalized) <= 200000000:
            return False
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
