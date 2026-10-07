import re
from ..metadata import IdMetadata
from ..util import validate_regexp


class OldIdentityCard:
    """
    Greece Identity Card, the old one.
    Metadata counts seven significant characters: one Greek letter and six digits.
    Validation accepts the compact layout or an optional hyphen after the letter (seven or eight characters).
    https://en.wikipedia.org/wiki/National_identification_number#Greece
    """
    METADATA = IdMetadata(**{
        'iso3166_alpha2': 'GR',
        # Significant characters only; separators are excluded.
        'min_length': 7,
        'max_length': 7,
        'parsable': False,
        'checksum': False,
        'regexp': re.compile(r'^[ΑΒΓΔΕΖΗΘΙΚΛΜΝΞΟΠΡΣΤΥΦΧΨΩ]-?\d{6}$'),
        'alias_of': None,
        'names': ['Identity Card Number'],
        'links': ['https://en.wikipedia.org/wiki/National_identification_number#Greece',
                  'https://en.wikipedia.org/wiki/Greek_identity_card'],
        'deprecated': True,
        'country_name': 'Greece',
        'id_type': 'Identity Card Number (Old)',
        'official_name': 'Δελτίο Ταυτότητας',
        'display_format': 'L-######',
        'example': 'Χ-123456',
        'checksum_algorithm': None,
        'masks': ('L-######', 'L######')
    })

    @staticmethod
    def validate(id_number: str) -> bool:
        """
        Validate with regexp
        """
        return validate_regexp(id_number, OldIdentityCard.METADATA.regexp)
