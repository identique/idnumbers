import re
from types import SimpleNamespace
from ..util import validate_regexp


class TaxNumber:
    """
    Cyprus tax number format
    https://en.wikipedia.org/wiki/VAT_identification_number
    https://www.oecd.org/tax/automatic-exchange/crs-implementation-and-assistance/tax-identification-numbers/Cyprus-TIN.pdf
    https://docs.oracle.com/en/cloud/saas/financials/22d/faitx/belgium.html#s20077698

    """
    METADATA = SimpleNamespace(**{
        'iso3166_alpha2': 'CY',
        'min_length': 9,
        'max_length': 9,
        'parsable': False,
        'checksum': True,
        'regexp': re.compile(r'^\d{8}[A-Z]$'),
        'alias_of': None,
        'names': ['tax number',
                  'Αριθμός Εγγραφής',
                  'ΦΠΑ',
                  'Φ.Π.Α.',
                  'phi. pi. a.',
                  'Arithmós Engraphḗs',
                  'φορολογικού κωδικού',
                  'φορολογική ταυτότητα',
                  'κωδικός φορολογικού μητρώου',
                  'αριθμός φορολογικού μητρώου',
                  'vergi kimlik numarası',
                  'vergi kimlik kodu'],
        'links': ['https://docs.oracle.com/en/cloud/saas/financials/22d/faitx/belgium.html#s20077698',
                  'https://en.wikipedia.org/wiki/VAT_identification_number',
                  'https://www.oecd.org/tax/automatic-exchange/crs-implementation-and-assistance/'
                  'tax-identification-numbers/Cyprus-TIN.pdf'],
        'deprecated': False
    })

    NUM_MAP = {0: 1, 1: 0, 2: 5, 3: 7, 4: 9, 5: 13, 6: 15, 7: 17, 8: 19, 9: 21}

    @staticmethod
    def validate(id_number: str) -> bool:
        """validate the id"""
        if not validate_regexp(id_number, TaxNumber.METADATA.regexp):
            return False
        return TaxNumber.checksum(id_number)

    @staticmethod
    def checksum(id_number: str) -> bool:
        """
        sum even as v1
        sum mapped odd as v2
        check = chr((v1 + v2) mod 26) + 65)
        src: https://ec.europa.eu/taxation_customs/tin/specs/FS-TIN%20Algorithms-Public.docx?v=1649548800030
        src: https://github.com/identique/idnumbers/files/11182565/FS-TIN.Algorithms-Public.docx (backup)
        """
        if not validate_regexp(id_number, TaxNumber.METADATA.regexp):
            return False
        numbers = [int(char) for char in id_number[:-1]]
        v1 = sum([numbers[idx] for idx in range(1, 8, 2)])
        v2 = sum([TaxNumber.NUM_MAP[numbers[idx]] for idx in range(0, 8, 2)])
        check_char = chr((v1 + v2) % 26 + 65)
        return check_char == id_number[-1]

    @staticmethod
    def is_individual(id_number: str) -> bool:
        return id_number[0] == '0' or id_number[0] == '9'
