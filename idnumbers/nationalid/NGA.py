import re
from types import SimpleNamespace


class NationalID:
    """
    Nigeria national ID number format
    https://en.wikipedia.org/wiki/National_identification_number#Nigeria
    """
    METADATA = SimpleNamespace(**{
        'iso3166_alpha2': 'NG',
        # length without insignificant chars
        'min_length': 11,
        'max_length': 11,
        # has parse function
        'parsable': False,
        # has checksum function
        'checksum': False,
        # regular expression to validate the id
        'regexp': re.compile(r'^\d{11}$')
    })

    @staticmethod
    def validate(id_number: str) -> bool:
        """
        Validate the NGA id number
        """
        if not isinstance(id_number, str):
            id_number = repr(id_number)
        return NationalID.METADATA.regexp.search(id_number) is not None
