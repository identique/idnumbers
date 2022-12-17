import re
from types import SimpleNamespace


"""
Nigeria national ID number format
https://en.wikipedia.org/wiki/National_identification_number#Nigeria
"""
METADATA = SimpleNamespace(**{
    'iso3166_alpha2': 'NG',
    # length without insignificant chars
    'min_length': 11,
    'max_length': 11,
    # is id parsable
    'parsable': False,
    # does id has checksum
    'checksum': False,
    # regular expression to validate the id
    'regexp': re.compile(r'^\d{11}$')
})


def validate(id_number: str) -> bool:
    """
    Validate the NGA id number
    """
    if not isinstance(id_number, str):
        id_number = repr(id_number)
    return METADATA.regexp.search(id_number) is not None
