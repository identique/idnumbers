import re
from types import SimpleNamespace
from typing import Optional
from ..util import CHECK_DIGIT, alias_of, validate_regexp
from .util import normalize


class TaxFileNumber:
    """
    Australia tax file number format
    Note: Australian law specifically prohibits the use of the TFN as a national identification number
    https://en.wikipedia.org/wiki/National_identification_number#Australia
    https://en.wikipedia.org/wiki/Tax_file_number
    https://www.ato.gov.au/General/What-is-a-tax-file-number----Easy-Read/
    https://en-academic.com/dic.nsf/enwiki/436130
    """
    METADATA = SimpleNamespace(**{
        'iso3166_alpha2': 'AU',
        # length without insignificant chars
        'min_length': 8,
        'max_length': 9,
        # has parse function
        'parsable': False,
        # has checksum function
        'checksum': True,
        # regular expression to validate the id
        'regexp': re.compile(r'^(\d{9}|\d{8})$'),
        'alias_of': None,
        'names': ['Tax file number',
                  'TFN'],
        'links': [
            'https://en.wikipedia.org/wiki/National_identification_number#Australia',
            'https://en.wikipedia.org/wiki/Tax_file_number',
            'https://www.ato.gov.au/General/What-is-a-tax-file-number----Easy-Read/',
            'https://en-academic.com/dic.nsf/enwiki/436130'],
        'deprecated': False
    })

    MULTIPLIER = [1, 4, 3, 7, 5, 8, 6, 9, 10]
    """The magic multiplier for checksum"""

    @staticmethod
    def validate(id_number: str) -> bool:
        """
        Validate the AUS tax file number
        """
        if not validate_regexp(id_number, TaxFileNumber.METADATA.regexp):
            return False
        return TaxFileNumber.checksum(id_number) == 0

    @staticmethod
    def checksum(id_number: str) -> Optional[CHECK_DIGIT]:
        if not validate_regexp(id_number, TaxFileNumber.METADATA.regexp):
            return None
        """algorithm: https://en.wikipedia.org/wiki/Tax_file_number#Check_digit"""
        normalized = normalize(id_number)
        if len(normalized) == 8:
            normalized = normalized[0:7] + '0' + normalized[7]
        number_list = [int(char) for char in list(normalized)]
        return sum([value * TaxFileNumber.MULTIPLIER[index] for (index, value) in enumerate(number_list)]) % 11


TFN = alias_of(TaxFileNumber)
"""alias of TaxFileNumber"""
