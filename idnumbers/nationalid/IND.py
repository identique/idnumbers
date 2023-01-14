import re
from types import SimpleNamespace
from .util import validate_regexp, verhoeff_check


def normalize(id_number: str) -> str:
    """strip out useless characters/whitespaces"""
    return re.sub(r'[ -]', '', id_number)


class NationalID:
    """
    India National ID number format, UID
    https://en.wikipedia.org/wiki/National_identification_number#India
    https://archive.org/details/Aadhaar_numbering_scheme/page/n12/mode/1up?view=theater
    https://en.wikipedia.org/wiki/Verhoeff_algorithm#Table-based_algorithm
    """
    METADATA = SimpleNamespace(**{
        'iso3166_alpha2': 'IN',
        'min_length': 12,
        'max_length': 12,
        'parsable': False,
        'checksum': True,
        'regexp': re.compile(r'^[2-9]\d{3}[ -]?\d{4}[ -]?\d{4}$')
    })

    @staticmethod
    def validate(id_number: str) -> bool:
        """
        Validate the id number
        """
        return NationalID.checksum(id_number)

    @staticmethod
    def checksum(id_number) -> bool:
        """use verhoeff checksum"""
        if not validate_regexp(id_number, NationalID.METADATA.regexp):
            return False
        return verhoeff_check([int(char) for char in normalize(id_number)])
