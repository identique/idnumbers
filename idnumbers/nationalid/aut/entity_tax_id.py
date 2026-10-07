import re
from types import SimpleNamespace
from ..util import validate_regexp


def normalize(id_number: str) -> str:
    """strip out useless characters/whitespaces"""
    return re.sub(r'[-/ ]', '', id_number)


class EntityTaxIDNumber:
    """
    Austrian UID: the local portion is U followed by eight digits, without the AT country code.

    The official BMF construction rules are linked in METADATA.links.
    """
    METADATA = SimpleNamespace(**{
        'iso3166_alpha2': 'AT',
        # length without insignificant chars
        'min_length': 9,
        'max_length': 9,
        # has parse function
        'parsable': False,
        # has checksum function
        'checksum': True,
        # regular expression to validate the id
        'regexp': re.compile(r'^(U\d{2}[- ]?\d{3}[ /]?\d{3})$'),
        'alias_of': None,
        'names': ['Entities Tax ID number', 'UID', 'Umsatzsteuer-Identifikationsnummer', 'VAT'],
        'links': ['https://www.finanz.at/en/taxes/vat-number/',
                  'https://www.glasbenamatica.org/wp-content/uploads/2017/05/TIN_-_country_sheet_AT_en.pdf',
                  'https://taxid.pro/docs/countries/austria',
                  'https://www.bmf.gv.at/dam/jcr:d6794f8f-d321-43df-9840-1a841f9bf5dc/'
                  'BMF_UID_Konstruktionsregeln_Stand_November%202020.pdf'],
        'deprecated': False
    })

    @staticmethod
    def validate(id_number: str) -> bool:
        """
        Validate the tax id number
        """
        if not validate_regexp(id_number, EntityTaxIDNumber.METADATA.regexp):
            return False
        return EntityTaxIDNumber.checksum(id_number)

    @staticmethod
    def checksum(id_number: str) -> bool:
        if not validate_regexp(id_number, EntityTaxIDNumber.METADATA.regexp):
            return False
        # BMF UID construction rules (November 2020), Austria; see METADATA.links.
        normalized = normalize(id_number)
        numbers = [int(char) for char in list(normalized[1:])]
        total = 4
        # since we removed the first char, the index of C2 = 0
        for (index, value) in enumerate(numbers[:-1]):
            if index % 2 == 0:
                total += value
            else:
                si = int(value / 5) + (value * 2) % 10
                total += si
        checksum = (10 - total % 10) % 10
        return checksum == numbers[-1]
