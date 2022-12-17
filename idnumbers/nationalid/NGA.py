import re
from types import SimpleNamespace


"""
Nigeria national ID number format
https://en.wikipedia.org/wiki/National_identification_number#Nigeria
"""
METADATA = SimpleNamespace(**{
    'iso3166_alpha2': 'NG',
    'min_length': 11,
    'max_length': 11,
    'parsable': False,
    'checksum': False,
    'regexp': re.compile(r'^\d{11}$')
})


def validate(id_number: str) -> bool:
    """
    Validate the NGA id number
    """
    if not isinstance(id_number, str):
        id_number = repr(id_number)
    return METADATA.regexp.search(id_number) is not None
