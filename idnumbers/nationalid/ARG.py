import re
from types import SimpleNamespace
from .util import validate_regexp


class NationalID:
    """
    Argentina National ID number
    https://www.protecto.ai/argentina-national-identity-number-download-sample-data-for-testing/
    https://en.wikipedia.org/wiki/Documento_Nacional_de_Identidad_(Argentina)
    """
    METADATA = SimpleNamespace(**{
        'iso3166_alpha2': 'AR',
        'min_length': 10,
        'max_length': 10,
        'parsable': False,
        'checksum': False,
        'regexp': re.compile(r'^(?P<first_section>\d{2})'
                             r'(\.)'
                             r'(?P<second_section>\d{3})'
                             r'(\.)'
                             r'(?P<third_section>\d{3})$')
    })

    @staticmethod
    def validate(id_number: str) -> bool:
        """
        Validate the ARG id number
        """
        return validate_regexp(id_number, NationalID.METADATA.regexp)
