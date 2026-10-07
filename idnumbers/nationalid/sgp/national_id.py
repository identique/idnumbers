import re
from ..metadata import IdMetadata
from ..util import weighted_modulus_digit, validate_regexp


class NationalID:
    """
    SGP National ID number format, UIN, FIN
    https://en.wikipedia.org/wiki/National_identification_number#Singapore
    https://www.ngiam.net/NRIC/NRIC_numbers.pdf
    python version of https://github.com/IonBazan/NRIC
    M series FIN (issued from 1 January 2022):
    https://www.ica.gov.sg/news-and-publications/media-releases/media-release/new-m-fin-series-to-be-introduced-from-1-january-2022
    https://github.com/opengovsg/FormSG/blob/develop/packages/shared/utils/nric-validation.ts
    """
    METADATA = IdMetadata(**{
        'iso3166_alpha2': 'SG',
        'min_length': 9,
        'max_length': 9,
        'parsable': False,
        'checksum': True,
        'regexp': re.compile(r'^(?P<type>[STFGM])'
                             r'(?P<sn>\d{7})'
                             r'(?P<checksum>[A-Z])$'),
        'alias_of': None,
        'names': ['National ID Number',
                  'NRIC',
                  'UIN',
                  'FIN'],
        'links': ['https://en.wikipedia.org/wiki/National_identification_number#Singapore',
                  'https://www.ngiam.net/NRIC/NRIC_numbers.pdf',
                  'https://www.ica.gov.sg/news-and-publications/media-releases/media-release/'
                  'new-m-fin-series-to-be-introduced-from-1-january-2022',
                  'https://github.com/opengovsg/FormSG/blob/develop/packages/shared/utils/nric-validation.ts'],
        'deprecated': False
    })

    MAGIC_MULTIPLIER = [2, 7, 6, 5, 4, 3, 2]
    CHECKSUM_MAP = {
        'S': 'JZIHGFEDCBA',
        'T': 'GFEDCBAJZIH',
        'F': 'XWUTRQPNMLK',
        'G': 'RQPNMLKXWUT',
        'M': 'XWUTRQPNJLK'
    }
    SERIES_OFFSET = {'M': 3}
    """
    The start constant added to the weighted sum before the modulus 11, by series. The M series adds 3
    (GovTech FormSG isMFinSeriesValid). The +4 of the T and G series is already folded into their rotated
    CHECKSUM_MAP tables, and the S and F series add 0, so they are not listed here.
    """

    @staticmethod
    def validate(id_number: str) -> bool:
        """
        Validate the SGP id number
        """
        if not validate_regexp(id_number, NationalID.METADATA.regexp):
            return False
        return NationalID.checksum(id_number)

    @staticmethod
    def checksum(id_number: str) -> bool:
        """
        algorithm from:
        https://www.ngiam.net/NRIC/NRIC_numbers.pdf
        https://github.com/IonBazan/NRIC
        https://github.com/opengovsg/FormSG/blob/develop/packages/shared/utils/nric-validation.ts
        """
        if not validate_regexp(id_number, NationalID.METADATA.regexp):
            return False
        series = id_number[0]
        checksum = id_number[-1]
        # it uses modulus 11 algorithm with magic numbers
        numbers = [int(char) for char in id_number[1:-1]]
        modulus = (weighted_modulus_digit(numbers, NationalID.MAGIC_MULTIPLIER, 11, True)
                   + NationalID.SERIES_OFFSET.get(series, 0)) % 11
        return checksum == NationalID.CHECKSUM_MAP[series][modulus]
