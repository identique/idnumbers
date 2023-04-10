import re
from types import SimpleNamespace
from ..util import validate_regexp


def normalize(id_number):
    """strip out useless characters/whitespaces"""
    return re.sub(r'[-/ ]', '', id_number)


class EntityTaxIDNumber:
    """
    Austria tax id number format
    https://validatetin.com/austria/
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
        'regexp': re.compile(r'^([A-Z]\d{2}[- ]?\d{3}[ /]?\d{3})$'),  # is the first char always 'U'?
        'alias_of': None,
        'names': ['Entities Tax ID number', 'UID', 'Umsatzsteuer-Identifikationsnummer', 'VAT'],
        'links': ['https://www.finanz.at/en/taxes/vat-number/',
                  'https://www.glasbenamatica.org/wp-content/uploads/2017/05/TIN_-_country_sheet_AT_en.pdf',
                  'https://taxid.pro/docs/countries/austria',
                  'https://www.bmf.gv.at/dam/jcr:9f9f8d5f-5496-4886-aa4f-81a4e39ba83e/BMF_UID_Konstruktionsregeln.pdf'],
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
        # https://www.bmf.gv.at/dam/jcr:9f9f8d5f-5496-4886-aa4f-81a4e39ba83e/BMF_UID_Konstruktionsregeln.pdf
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
