import re
from types import SimpleNamespace
from ..util import validate_regexp
from .util import normalize


class RGNumber:
    """
    Brazil Registro Geral Number
    https://en.wikipedia.org/wiki/National_identification_number#Brazil
    https://en.wikipedia.org/wiki/Brazilian_identity_card
    """
    METADATA = SimpleNamespace(**{
        'iso3166_alpha2': 'BR',
        # length without insignificant chars
        'min_length': 9,
        'max_length': 9,
        'parsable': False,
        'checksum': True,
        'regexp': re.compile(r'^(\d{2}\.\d{3}\.\d{3}-[\d|X])$'),
        'alias_of': None,
        'names': ['RG number',
                  'Registro Geral number'],
        'links': ['https://en.wikipedia.org/wiki/National_identification_number#Brazil',
                  'https://en.wikipedia.org/wiki/Brazilian_identity_cards'],
        'deprecated': False
    })

    @staticmethod
    def validate(id_number: str) -> bool:
        """
        Validate the BRA Registro Geral Number
        """
        if not validate_regexp(id_number, RGNumber.METADATA.regexp):
            return False
        return RGNumber.checksum(id_number)

    MULTIPLIER = [2, 3, 4, 5, 6, 7, 8, 9]

    @staticmethod
    def checksum(id_number: str) -> bool:
        """Validate RG number checksum"""
        normalized = normalize(id_number)
        number_list = [int(char) for char in list(normalized[:8])]
        # X is equal to 11 in check digit
        check_digit = 11 if normalized[8] == 'X' else int(normalized[8])
        total = sum([value * RGNumber.MULTIPLIER[index] for (index, value) in enumerate(number_list)])
        return True if ((total + check_digit * 100) % 11) == 0 else False
