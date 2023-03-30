import re
from types import SimpleNamespace

from ..util import validate_regexp


class NationalID:
    """
    Papua New Guinea national id, NID
    https://en.wikipedia.org/wiki/National_identification_number#Papua_New_Guinea
    """
    METADATA = SimpleNamespace(**{
        'iso3166_alpha2': 'PG',
        # length without insignificant chars
        'min_length': 10,
        'max_length': 10,
        # has parse function
        'parsable': False,
        # has checksum function
        'checksum': False,
        # regular expression to validate the id
        'regexp': re.compile(r'^\d{10}$'),
        'alias_of': None,
        'names': ['National ID Number',
                  'NID'],
        'links': ['https://en.wikipedia.org/wiki/National_identification_number#Papua_New_Guinea'],
        'deprecated': False
    })

    @staticmethod
    def validate(id_number: str) -> bool:
        """
        Validate the NID
        """
        return validate_regexp(id_number, NationalID.METADATA.regexp)
