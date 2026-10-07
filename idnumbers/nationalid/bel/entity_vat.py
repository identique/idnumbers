import re
from ..metadata import IdMetadata
from ..util import validate_regexp
from .util import calc_check_digits


class EntityVAT:
    """
    Belgium enterprise (VAT) number format
    https://en.wikipedia.org/wiki/VAT_identification_number
    https://docs.oracle.com/en/cloud/saas/financials/22d/faitx/belgium.html#s20077698

    The number has 10 digits: 8 digits and 2 check digits (``97 - (the 8 digits mod 97)``).
    The first digit is 0 or 1: the 0-series is used up, and the 1-series began on 19 September 2023
    (FOD Economie). The old 9-digit form is the same number with the leading 0 left out, so a
    9-digit input has an implied leading 0 and its first digit may be any digit.
    """
    METADATA = IdMetadata(**{
        'iso3166_alpha2': 'BE',
        'min_length': 9,
        'max_length': 10,
        'parsable': False,
        'checksum': True,
        'regexp': re.compile(r'^(?:[01]\d{9}|\d{9})$'),
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
                  'https://www.vatcalc.com/belgium/belgian-vat-number-format-changes/',
                  'https://news.economie.fgov.be/228778-ondernemingsnummers-beginnen-nu-ook-met-het-cijfer-1/'],
        'deprecated': False,
        'country_name': 'Belgium',
        'id_type': 'VAT Identification Number',
        'official_name': 'BTW identificatienummer',
        'display_format': '0#########',
        'example': '0123456749',
        'checksum_algorithm': 'Mod 97 (the last two digits are 97 - (the first eight digits mod 97))',
        'masks': ('##########', '#########')
    })

    @staticmethod
    def validate(id_number: str) -> bool:
        """validate the id"""
        if not validate_regexp(id_number, EntityVAT.METADATA.regexp):
            return False
        return EntityVAT.checksum(id_number)

    @staticmethod
    def checksum(id_number: str) -> bool:
        """
        calculated as the remainder of dividing xxxxxxxxxx by 97
        (if the remainder is 0, the check number is set to 97)
        """
        if not validate_regexp(id_number, EntityVAT.METADATA.regexp):
            return False
        return int(id_number[-2:]) == calc_check_digits(int(id_number[:-2]))
