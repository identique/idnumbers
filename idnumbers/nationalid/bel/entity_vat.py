import re
from types import SimpleNamespace
from ..util import validate_regexp
from .util import calc_check_digits


class EntityVAT:
    """
    Belgium National register number format
    https://en.wikipedia.org/wiki/VAT_identification_number
    https://docs.oracle.com/en/cloud/saas/financials/22d/faitx/belgium.html#s20077698

    """
    METADATA = SimpleNamespace(**{
        'iso3166_alpha2': 'BE',
        'min_length': 9,
        'max_length': 10,
        'parsable': False,
        'checksum': True,
        'regexp': re.compile(r'^\d{9,10}$'),
        'alias_of': None,
        'names': ['tax registration numbers',
                  'Belgium BE VAT',
                  'TVA',
                  'BTW identificatienummer',
                  'Numéro de TVA',
                  'BTW-nr',
                  'Mwst-nr'],
        'links': ['https://docs.oracle.com/en/cloud/saas/financials/22d/faitx/belgium.html#s20077698',
                  'https://en.wikipedia.org/wiki/VAT_identification_number',
                  'https://www.vatcalc.com/belgium/belgian-vat-number-format-changes/'],
        'deprecated': False
    })

    @staticmethod
    def validate(id_number: str) -> bool:
        """validate the id"""
        if not validate_regexp(id_number, EntityVAT.METADATA.regexp):
            return False
        return EntityVAT.checksum(id_number)

    @staticmethod
    def checksum(id_number) -> bool:
        """
        calculated as the remainder of dividing xxxxxxxxxx by 97
        (if the remainder is 0, the check number is set to 97)
        """
        if not validate_regexp(id_number, EntityVAT.METADATA.regexp):
            return False
        return int(id_number[-2:]) == calc_check_digits(int(id_number[:-2]))
