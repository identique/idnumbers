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
        # length without insignificant chars
        'min_length': 8,
        'max_length': 8,
        'parsable': False,
        'checksum': False,
        'regexp': re.compile(r'^(\d{2}[.]\d{3}[.]\d{3})$')

    })

    @staticmethod
    def validate(id_number: str) -> bool:
        """
        Validate the ARG id number
        """
        return validate_regexp(id_number, NationalID.METADATA.regexp)
