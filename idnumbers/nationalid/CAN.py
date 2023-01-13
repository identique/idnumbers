import re
from types import SimpleNamespace

from .util import validate_regexp


class SocialInsuranceNumber:
    """
    Canada social insurance number format
    https://en.wikipedia.org/wiki/National_identification_number#Canada
    """
    METADATA = SimpleNamespace(**{
        'iso3166_alpha2': 'CA',
        # length without insignificant chars
        'min_length': 9,
        'max_length': 9,
        # has parse function
        'parsable': False,
        # has checksum function
        'checksum': True,
        # regular expression to validate the id
        'regexp': re.compile(r'^\d{9}$')
    })

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
        MULTIPLIER = [1, 2, 1, 2, 1, 2, 1, 2, 1]
        number_list = [int(char) for char in list(id_number)]
        multiplied_list = [value * MULTIPLIER[index] for (index, value) in enumerate(number_list)]
        return sum([sum(divmod(num, 10)) for num in multiplied_list]) % 10 == 0
