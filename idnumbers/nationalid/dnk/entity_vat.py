import re
from types import SimpleNamespace
from ..util import validate_regexp, weighted_modulus_digit


class EntityVAT:
    """
    Entity VAT Number is called Momsregistreringsnummer or CVR nummer.
    https://www.oecd.org/tax/automatic-exchange/crs-implementation-and-assistance/tax-identification-numbers/Denmark-TIN.pdf
    https://wiki.scn.sap.com/wiki/display/CRM/Denmark
    CPR numbers issued after 1 October 2007 can have a different format meaning that the last digit is not a check digit
    and can therefore not be verified on the TIN on Europa web portal.
    """
    METADATA = SimpleNamespace(**{
        'iso3166_alpha2': 'DK',
        'min_length': 8,
        'max_length': 8,
        'parsable': False,
        'checksum': True,
        'regexp': re.compile(r'^\d{8}$'),
        'alias_of': None,
        'names': ['Entity VAT',
                  'CVR',
                  'SE',
                  'Momsregistreringsnummer'],
        'links': ['https://wiki.scn.sap.com/wiki/display/CRM/Denmark',
                  'https://www.oecd.org/tax/automatic-exchange/crs-implementation-and-assistance/'
                  'tax-identification-numbers/Denmark-TIN.pdf'],
        'deprecated': False
    })

    MULTIPLIER = [2, 7, 6, 5, 4, 3, 2, 1]

    @staticmethod
    def validate(id_number: str) -> bool:
        """
        Validate the id number
        """
        return EntityVAT.checksum(id_number)

    @staticmethod
    def checksum(id_number: str) -> bool:
        """ validate the CVR id"""
        if not validate_regexp(id_number, EntityVAT.METADATA.regexp):
            return False

        numbers = [int(char) for char in id_number]
        return weighted_modulus_digit(numbers, EntityVAT.MULTIPLIER, 11, True) == 0
