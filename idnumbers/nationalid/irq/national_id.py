import re
from ..metadata import IdMetadata
from ..util import validate_regexp


class NationalID:
    """
    Iraq National Card number. not enough docs to research.
    https://en.wikipedia.org/wiki/Iraq_National_Card
    """
    METADATA = IdMetadata(**{
        'iso3166_alpha2': 'IQ',
        'min_length': 12,
        'max_length': 12,
        'parsable': False,
        'checksum': False,
        'regexp': re.compile(r'^\d{12}$'),
        'alias_of': None,
        'names': ['National Card Number',
                  'البطاقة الوطنية',
                  'كارتى نيشتمانى'],
        'links': ['https://en.wikipedia.org/wiki/Iraq_National_Card'],
        'deprecated': False,
        'country_name': 'Iraq',
        'id_type': 'National Card Number',
        'official_name': 'البطاقة الوطنية',
        'display_format': '############',
        'example': '123456789012',
        'checksum_algorithm': None,
        'masks': ('############',)
    })

    @staticmethod
    def validate(id_number: str) -> bool:
        """
        Validate
        """
        return validate_regexp(id_number, NationalID.METADATA.regexp)
