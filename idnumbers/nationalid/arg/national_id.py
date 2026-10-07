import re
from types import SimpleNamespace
from ..util import validate_regexp


class NationalID:
    """
    Argentina National ID number
    https://www.protecto.ai/argentina-national-identity-number-download-sample-data-for-testing/
    https://en.wikipedia.org/wiki/Documento_Nacional_de_Identidad_(Argentina%29

    A DNI has 7 or 8 digits (numbers below 10 million have 7), optionally grouped with dots as ``#.###.###`` or
    ``##.###.###``, see python-stdnum ``stdnum/ar/dni.py``
    https://github.com/arthurdejong/python-stdnum/blob/master/stdnum/ar/dni.py
    """
    METADATA = SimpleNamespace(**{
        'iso3166_alpha2': 'AR',
        # length without insignificant chars
        'min_length': 7,
        'max_length': 8,
        'parsable': False,
        'checksum': False,
        'regexp': re.compile(r'^(\d{1,2}\.?\d{3}\.?\d{3})$'),
        'alias_of': None,
        'names': ['Documento Nacional de Identidad',
                  'DNI'],
        'links': ['https://www.protecto.ai/argentina-national-identity-number-download-sample-data-for-testing/',
                  'https://en.wikipedia.org/wiki/Documento_Nacional_de_Identidad_(Argentina)',
                  'https://github.com/arthurdejong/python-stdnum/blob/master/stdnum/ar/dni.py'],
        'deprecated': False

    })

    @staticmethod
    def validate(id_number: str) -> bool:
        """
        Validate the ARG id number
        """
        return validate_regexp(id_number, NationalID.METADATA.regexp)
