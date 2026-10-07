import re
from ..metadata import IdMetadata

from ..util import validate_regexp


class SocialInsuranceNumber:
    """
    Canada social insurance number format
    https://en.wikipedia.org/wiki/National_identification_number#Canada
    """
    METADATA = IdMetadata(**{
        'iso3166_alpha2': 'CA',
        # length without insignificant chars
        'min_length': 9,
        'max_length': 9,
        # has parse function
        'parsable': False,
        # has checksum function
        'checksum': True,
        # regular expression to validate the id
        'regexp': re.compile(r'^\d{9}$'),
        'alias_of': None,
        'names': ['Social Insurance Number',
                  'SIN'],
        'links': ['https://en.wikipedia.org/wiki/National_identification_number#Canada'],
        'deprecated': False,
        'country_name': 'Canada',
        'id_type': 'Social Insurance Number',
        'official_name': None,
        'display_format': '#########',
        'example': '123456782',
        'checksum_algorithm': 'Luhn (mod 10)',
        'masks': ('#########',)
    })

    MULTIPLIER = [1, 2, 1, 2, 1, 2, 1, 2, 1]

    @staticmethod
    def validate(id_number: str) -> bool:
        """
        Validate the CAN id number
        """
        if not validate_regexp(id_number, SocialInsuranceNumber.METADATA.regexp):
            return False
        return SocialInsuranceNumber.checksum(id_number)

    @staticmethod
    def checksum(id_number: str) -> bool:
        """
        Validate social insurance number checksum digits
        http://www.straightlineinternational.com/docs/vaildating_canadian_sin.pdf
        """

        number_list = [int(char) for char in list(id_number)]
        multiplied_list = [value * SocialInsuranceNumber.MULTIPLIER[index] for (index, value) in enumerate(number_list)]
        return sum([sum(divmod(num, 10)) for num in multiplied_list]) % 10 == 0
