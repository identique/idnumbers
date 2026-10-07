import re
from ..metadata import IdMetadata
from ..util import validate_regexp
from .util import normalize


class RGNumber:
    """
    Brazil Registro Geral Number
    https://en.wikipedia.org/wiki/National_identification_number#Brazil
    https://en.wikipedia.org/wiki/Brazilian_identity_card
    """
    METADATA = IdMetadata(**{
        'iso3166_alpha2': 'BR',
        # length without insignificant chars
        'min_length': 9,
        'max_length': 9,
        'parsable': False,
        'checksum': True,
        'regexp': re.compile(r'^(\d{2}\.\d{3}\.\d{3}-[\dX])$'),
        'alias_of': None,
        'names': ['RG number',
                  'Registro Geral number'],
        'links': ['https://en.wikipedia.org/wiki/National_identification_number#Brazil',
                  'https://en.wikipedia.org/wiki/Brazilian_identity_cards'],
        'deprecated': False,
        'country_name': 'Brazil',
        'id_type': 'General Registry Number',
        'official_name': 'Registro Geral',
        'display_format': '##.###.###-X',
        'example': '12.345.678-2',
        'checksum_algorithm': 'Weighted sum mod 11 (weights 2-9 over the first eight digits, the check digit weighted '
                              '100; X counts as 11)',
        'masks': ('##.###.###-X',)
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
        """Validate RG number checksum, False when the input is not a well-formed RG number"""
        if not validate_regexp(id_number, RGNumber.METADATA.regexp):
            return False
        normalized = normalize(id_number)
        number_list = [int(char) for char in list(normalized[:8])]
        # X is equal to 11 in check digit
        if normalized[8] == 'X':
            check_digit = 11
        else:
            check_digit = int(normalized[8])
        total = sum([value * RGNumber.MULTIPLIER[index] for (index, value) in enumerate(number_list)])
        return True if ((total + check_digit * 100) % 11) == 0 else False
