import re
from ..metadata import IdMetadata
from ..util import validate_regexp


class PersonalNumber:
    """
    Georgia personal number format

    The personal number is 11 digits and may start with 0. No public
    check-digit algorithm is documented, so only the length and the digits are
    checked. The same 11 digit number is used as the tax identification number
    of a Georgian citizen.

    A 9 digit number is not a personal number: it is an identity document
    number, or a tax identification number issued to a non-citizen or a company.

    https://en.wikipedia.org/wiki/National_identification_number#Georgia
    https://www.oecd.org/tax/automatic-exchange/crs-implementation-and-assistance/tax-identification-numbers/Georgia-TIN.pdf
    """
    METADATA = IdMetadata(**{
        'iso3166_alpha2': 'GE',
        'min_length': 11,
        'max_length': 11,
        'parsable': False,
        'checksum': False,
        'regexp': re.compile(r'^\d{11}$'),
        'alias_of': None,
        'names': ['personal number'],
        'links': [
            'https://en.wikipedia.org/wiki/National_identification_number#Georgia',
            'https://www.oecd.org/tax/automatic-exchange/crs-implementation-and-assistance/tax-identification-numbers/Georgia-TIN.pdf',
        ],
        'deprecated': False,
        'country_name': 'Georgia',
        'id_type': 'Personal Number',
        'official_name': None,
        'display_format': '###########',
        'example': '12345678901',
        'checksum_algorithm': None,
        'masks': ('###########',)
    })

    @staticmethod
    def validate(id_number: str) -> bool:
        """
        Validate personal number
        """
        return validate_regexp(id_number, PersonalNumber.METADATA.regexp)
