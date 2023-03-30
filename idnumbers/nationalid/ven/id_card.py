import re
from types import SimpleNamespace

from ..util import validate_regexp


class IDCardNumber:
    """
    Venezuela ID card number
    https://en.wikipedia.org/wiki/National_identification_number#Venezuela
    """
    METADATA = SimpleNamespace(**{
        'iso3166_alpha2': 'VE',
        # length without insignificant chars
        'min_length': 9,
        'max_length': 9,
        # has parse function
        'parsable': False,
        # has checksum function
        'checksum': False,
        # regular expression to validate the id
        'regexp': re.compile(r'^V ?\d{2}\.?\d{3}\.?\d{3}$'),
        'alias_of': None,
        'names': ['ID Card Number',
                  'Cédula de Identidad'],
        'links': ['https://en.wikipedia.org/wiki/National_identification_number#Venezuela'],
        'deprecated': False
    })

    @staticmethod
    def validate(id_number: str) -> bool:
        """
        Validate
        """
        return validate_regexp(id_number, IDCardNumber.METADATA.regexp)
