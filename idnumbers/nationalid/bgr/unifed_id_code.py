import re
from ..metadata import IdMetadata
from typing import Optional, cast

from ..util import validate_regexp, CHECK_DIGIT, weighted_modulus_digit


class UnifiedIdCode:
    """
    Bulgaria unified identification code, UIC
    https://validatetin.com/bulgaria/
    """
    METADATA = IdMetadata(**{
        'iso3166_alpha2': 'BG',
        # length without insignificant chars
        'min_length': 9,
        'max_length': 13,
        'parsable': False,
        'checksum': True,
        'regexp': re.compile(r'^(\d{9}|\d{13})$'),
        'alias_of': None,
        'names': ['Unified Identification Code',
                  'UIC',
                  'EIK',
                  'BULSTAT',
                  'ЕИК',
                  'БУЛСТАТ'],
        'links': ['https://validatetin.com/bulgaria/',
                  'https://taxid.pro/docs/countries/bulgaria',
                  'https://www.wikidata.org/wiki/Property:P8894',
                  'https://www.wikidata.org/wiki/Wikidata:Property_proposal/EIK',
                  'https://tsvetanv.wordpress.com/2011/04/01/eik/',
                  'https://github.com/mirovit/eik-validator/blob/master/src/EIKValidator/EIKValidator.php',
                  'http://bsv-bg.com/%D0%BA%D0%BE%D0%BD%D1%82%D1%80%D0%BE%D0%BB%D0%BD%D0%B8-'
                  '%D1%86%D0%B8%D1%84%D1%80%D0%B8-%D0%BF%D0%BE%D0%BB%D0%B7%D0%B2%D0%B0%D0%BD%D0%B8-'
                  '%D0%B2-%D0%B1%D1%8A%D0%BB%D0%B3%D0%B0%D1%80%D0%B8%D1%8F/',
                  'https://bg.wikipedia.org/wiki/%D0%95%D0%B4%D0%B8%D0%BD%D0%B5%D0%BD_'
                  '%D0%B8%D0%B4%D0%B5%D0%BD%D1%82%D0%B8%D1%84%D0%B8%D0%BA%D0%B0%D1%86%D0%B8%D0%BE%D0%BD%D0%B5%D0%BD_'
                  '%D0%BA%D0%BE%D0%B4'],
        'deprecated': False,
        'country_name': 'Bulgaria',
        'id_type': 'Unified Identification Code',
        'official_name': 'Единен идентификационен код',
        'display_format': '#########(####)',
        'example': '123456786',
        'checksum_algorithm': 'Weighted sum mod 11 in two passes (weights 1-8, then 3-10; a remainder of 10 in both '
                              'passes becomes 0); the 13th digit of a 13-digit code uses weights 2, 7, 3, 5 then 4, 9, '
                              '5, 7',
        'masks': ('#########', '#############')
    })

    WEIGHTS9_1 = [1, 2, 3, 4, 5, 6, 7, 8]
    WEIGHTS9_2 = [3, 4, 5, 6, 7, 8, 9, 10]
    WEIGHTS13_1 = [2, 7, 3, 5]
    WEIGHTS13_2 = [4, 9, 5, 7]

    @staticmethod
    def validate(id_number: str) -> bool:
        """
        Validate the BGR id number

        A 13-digit code (BULSTAT of a branch) is valid only when its first nine digits are a valid 9-digit EIK
        and its 13th digit matches the check digit computed over digits 9 to 12.
        """
        if not validate_regexp(id_number, UnifiedIdCode.METADATA.regexp):
            return False
        if len(id_number) == 13 and not UnifiedIdCode.validate(id_number[:9]):
            return False
        check = UnifiedIdCode.checksum(id_number)
        return check is not None and str(check) == id_number[-1]

    @staticmethod
    def checksum(id_number: str) -> Optional[CHECK_DIGIT]:
        """
        Get the checksum digit, or None when the input is not a well-formed BGR id number

        9 digits: the 9th digit is the check digit of the first eight digits. The weighted sum with weights
        1..8 mod 11 is used; if it is 10, the weighted sum with weights 3..10 mod 11 is used; if that is also 10,
        the check digit is 0.

        13 digits: the 13th digit is the check digit of digits 9 to 12 (zero-based positions 8 to 11), with the same
        two-pass rule and the weights 2, 7, 3, 5 and then 4, 9, 5, 7. The first nine digits must additionally
        be a valid 9-digit EIK, which validate() checks.

        Sources:
        https://github.com/mirovit/eik-validator/blob/master/src/EIKValidator/EIKValidator.php
        https://tsvetanv.wordpress.com/2011/04/01/eik/
        bsv-bg.com, check digits used in Bulgaria (see METADATA.links)
        """
        if not validate_regexp(id_number, UnifiedIdCode.METADATA.regexp):
            return None
        if len(id_number) == 9:
            numbers = [int(i) for i in id_number[:-1]]
            weights = [UnifiedIdCode.WEIGHTS9_1, UnifiedIdCode.WEIGHTS9_2]
        else:
            numbers = [int(i) for i in id_number[8:12]]
            weights = [UnifiedIdCode.WEIGHTS13_1, UnifiedIdCode.WEIGHTS13_2]

        modulus1 = weighted_modulus_digit(numbers, weights[0], 11, True)
        if modulus1 < 10:
            return cast(CHECK_DIGIT, modulus1)
        modulus2 = weighted_modulus_digit(numbers, weights[1], 11, True)
        return cast(CHECK_DIGIT, modulus2 if modulus2 < 10 else 0)
