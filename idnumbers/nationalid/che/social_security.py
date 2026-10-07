import re
from ..metadata import IdMetadata
from ..util import validate_regexp, ean13_digit


def normalize(id_number: str) -> str:
    """strip out useless characters/whitespaces"""
    return re.sub(r'\.', '', id_number)


class SocialSecurityNumber:
    """
    Switzerland Social Security Number (AHV-Nr. [de] / No AVS [fr])
    https://en.wikipedia.org/wiki/National_identification_number#Switzerland

    The last digit is the EAN-13 check digit of the first 12 digits, the weights are 1 and 3:
    https://www.gs1.org/services/how-calculate-check-digit-manually
    python-stdnum implements the same check digit in stdnum/ch/ssn.py:
    https://github.com/arthurdejong/python-stdnum/blob/master/stdnum/ch/ssn.py

    eCH-0044 V4.1, section 3.2.6 (vnType), defines the number range 7560000000001 to 7569999999999
    (it does not describe the check digit):
    https://www.ech.ch/sites/default/files/dosvers/hauptdokument/STAN_d_DEF_2014-04-02_eCH-0044_V4.1_Datenstandard%20Austausch%20von%20Personenidentifikationen.pdf
    """
    METADATA = IdMetadata(**{
        'iso3166_alpha2': 'CH',
        # length without insignificant chars
        'min_length': 13,
        'max_length': 13,
        'parsable': False,
        'checksum': True,
        'regexp': re.compile(r'^756\.\d{4}\.\d{4}\.\d{2}$'),
        'alias_of': None,
        'names': ['Social Security Number',
                  'AHV-Nr.',
                  'No AVS'],
        'links': ['https://en.wikipedia.org/wiki/National_identification_number#Switzerland',
                  'https://www.gs1.org/services/how-calculate-check-digit-manually',
                  'https://github.com/arthurdejong/python-stdnum/blob/master/stdnum/ch/ssn.py',
                  'https://www.ech.ch/sites/default/files/dosvers/hauptdokument/'
                  'STAN_d_DEF_2014-04-02_eCH-0044_V4.1_Datenstandard%20Austausch%20von%20Personenidentifikationen.pdf'],
        'deprecated': False

    })

    @staticmethod
    def validate(id_number: str) -> bool:
        """validate the number"""
        return SocialSecurityNumber.checksum(id_number)

    @staticmethod
    def checksum(id_number: str) -> bool:
        """use EAN-13 to validate the number"""
        if not validate_regexp(id_number, SocialSecurityNumber.METADATA.regexp):
            return False
        # the regexp leaves exactly 13 ASCII digits once the dots are stripped
        normalized = normalize(id_number)
        numbers = [int(char) for char in normalized]
        return numbers[-1] == ean13_digit(numbers[:-1])
