import re
from types import SimpleNamespace
from ..util import validate_regexp


class BusinessID:
    """
    Switzerland business identification number (UID)
    https://www.bfs.admin.ch/bfs/en/home/registers/enterprise-register/enterprise-identification/uid-general.html
    """
    METADATA = SimpleNamespace(**{
        'iso3166_alpha2': 'CH',
        # length without insignificant chars
        'min_length': 12,
        'max_length': 12,
        'parsable': False,
        'checksum': False,
        'regexp': re.compile(r'^CHE-?\d{3}\.?\d{3}\.?\d{3}$'),
        'alias_of': None,
        'names': ['business identification number',
                  'UID'],
        'links': [
            'https://www.bfs.admin.ch/bfs/en/home/registers/enterprise-register/'
            'enterprise-identification/uid-general.html'
        ],
        'deprecated': False
    })

    @staticmethod
    def validate(id_number: str) -> bool:
        return validate_regexp(id_number, BusinessID.METADATA.regexp)
