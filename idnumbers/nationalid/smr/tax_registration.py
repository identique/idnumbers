import re
from types import SimpleNamespace

from ..util import validate_regexp


class TaxRegistrationNumber:
    """
    San Marino, entity tax registration number, COE number
    https://www.oecd.org/tax/automatic-exchange/crs-implementation-and-assistance/tax-identification-numbers/San-Marino-TIN.pdf
    """
    METADATA = SimpleNamespace(**{
        'iso3166_alpha2': 'SM',
        'min_length': 7,
        'max_length': 7,
        # length without insignificant chars
        'parsable': False,
        # has parse function
        'checksum': False,
        # has checksum function
        'regexp': re.compile(r'^SM\d{5}$'),
        # regular expression to validate the id
        'alias_of': None,
        'names': ['Entity Tax Registration Number',
                  'COE'],
        'links': ['https://www.oecd.org/tax/automatic-exchange/crs-implementation-and-assistance/'
                  'tax-identification-numbers/San-Marino-TIN.pdf'],
        'deprecated': False
    })

    @staticmethod
    def validate(id_number: str) -> bool:
        """
        Validate
        """
        return validate_regexp(id_number, TaxRegistrationNumber.METADATA.regexp)
