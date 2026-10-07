import re
from ..metadata import IdMetadata
from ..util import validate_regexp


class IdentityCard:
    """
    Greece Identity Card, the new one.
    Metadata counts eight significant characters: two letters and six digits.
    Validation accepts the compact layout or an optional hyphen after the letters (eight or nine characters).
    https://en.wikipedia.org/wiki/National_identification_number#Greece
    """
    METADATA = IdMetadata(**{
        'iso3166_alpha2': 'GR',
        # Significant characters only; separators are excluded.
        'min_length': 8,
        'max_length': 8,
        'parsable': False,
        'checksum': False,
        'regexp': re.compile(r'^[ΑΒΓΔΕΖΗΘΙΚΛΜΝΞΟΠΡΣΤΥΦΧΨΩABEZHIKMNOPTYX]{2}-?\d{6}$'),
        # They are two different char set, the former is Greek alphabet, the latter is Latin alphabet
        'alias_of': None,
        'names': ['Identity Card Number'],
        'links': ['https://en.wikipedia.org/wiki/National_identification_number#Greece',
                  'https://en.wikipedia.org/wiki/Greek_identity_card'],
        'deprecated': False,
        'country_name': 'Greece',
        'id_type': 'Identity Card Number',
        'official_name': 'Δελτίο Ταυτότητας',
        'display_format': 'LL-######',
        'example': 'AB-123456',
        'checksum_algorithm': None,
        'masks': ('LL-######', 'LL######')
    })

    @staticmethod
    def validate(id_number: str) -> bool:
        """
        Validate with regexp
        """
        return validate_regexp(id_number, IdentityCard.METADATA.regexp)
