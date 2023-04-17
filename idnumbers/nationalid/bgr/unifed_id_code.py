import re
from types import SimpleNamespace
from typing import Optional

from ..util import validate_regexp, CHECK_DIGIT, weighted_modulus_digit


class UnifiedIdCode:
    """
    Bulgaria unified identification code, UIC
    https://validatetin.com/bulgaria/
    """
    METADATA = SimpleNamespace(**{
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
                  'https://bg.wikipedia.org/wiki/%D0%95%D0%B4%D0%B8%D0%BD%D0%B5%D0%BD_'
                  '%D0%B8%D0%B4%D0%B5%D0%BD%D1%82%D0%B8%D1%84%D0%B8%D0%BA%D0%B0%D1%86%D0%B8%D0%BE%D0%BD%D0%B5%D0%BD_'
                  '%D0%BA%D0%BE%D0%B4'],
        'deprecated': False
    })

    WEIGHTS9_1 = [1, 2, 3, 4, 5, 6, 7, 8]
    WEIGHTS9_2 = [3, 4, 5, 6, 7, 8, 9, 10]
    WEIGHTS13_1 = [2, 7, 3, 5]
    WEIGHTS13_2 = [4, 9, 5, 7]

    @staticmethod
    def validate(id_number: str) -> bool:
        """
        Validate the BGR id number
        """
        if not validate_regexp(id_number, UnifiedIdCode.METADATA.regexp):
            return False
        check = UnifiedIdCode.checksum(id_number)
        return check is not None and str(check) == id_number[-1]

    @staticmethod
    def checksum(id_number: str) -> Optional[CHECK_DIGIT]:
        if not validate_regexp(id_number, UnifiedIdCode.METADATA.regexp):
            return None
        """
        Get the checksum digit
        python version of:
        https://github.com/mirovit/eik-validator/blob/master/src/EIKValidator/EIKValidator.php
        """
        if len(id_number) == 9:
            numbers = [int(i) for i in id_number[:-1]]
            weights = [UnifiedIdCode.WEIGHTS9_1, UnifiedIdCode.WEIGHTS9_2]
        else:
            numbers = [int(i) for i in id_number[0:4]]
            weights = [UnifiedIdCode.WEIGHTS13_1, UnifiedIdCode.WEIGHTS13_2]

        modulus1 = weighted_modulus_digit(numbers, weights[0], 11, True)
        if modulus1 < 10:
            return modulus1
        modulus2 = weighted_modulus_digit(numbers, weights[1], 11, True)
        return modulus2 if modulus2 < 10 else 0
