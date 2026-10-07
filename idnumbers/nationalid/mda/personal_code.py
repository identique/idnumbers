import re
from ..metadata import IdMetadata

from ..util import validate_regexp


class PersonalCode:
    """
    Moldova Personal Code, IDNP
    https://en.wikipedia.org/wiki/National_identification_number#Moldova
    """
    METADATA = IdMetadata(**{
        'iso3166_alpha2': 'MD',
        # length without insignificant chars
        'min_length': 13,
        'max_length': 13,
        # has parse function
        'parsable': False,
        # has checksum function
        'checksum': False,
        # regular expression to validate the id
        'regexp': re.compile(r'^\d{13}$'),
        'alias_of': None,
        'names': ['Personal Code',
                  'IDNP'],
        'links': ['https://en.wikipedia.org/wiki/National_identification_number#Moldova',
                  'https://ro.wikipedia.org/wiki/IDNP'],
        'deprecated': False,
        'country_name': 'Moldova',
        'id_type': 'Personal Code',
        'official_name': 'Identificatorul Numeric Personal',
        'display_format': '#############',
        'example': '1234567890123',
        'checksum_algorithm': None,
        'masks': ('#############',)
    })

    @staticmethod
    def validate(id_number: str) -> bool:
        """
        Validate the personal code
        """
        return validate_regexp(id_number, PersonalCode.METADATA.regexp)
