import re
from ..metadata import IdMetadata
from ..util import luhn_digit, validate_regexp


class CitizenCard:
    """
    Portuguese Citizen Card document number, in compact uppercase form.

    The AMA specification defines nine digits, two alphanumeric version characters and a
    final check digit. Letters are values 10 through 35, not separate decimal digits. The
    full-card checksum does not check the inner civil ID checksum or prove that a card was issued.
    """
    METADATA = IdMetadata(**{
        'iso3166_alpha2': 'PT',
        'min_length': 12,
        'max_length': 12,
        'parsable': False,
        'checksum': True,
        'regexp': re.compile(r'\A[0-9]{9}[A-Z0-9]{2}[0-9]\Z'),
        'alias_of': None,
        'names': ['Citizen Card', 'Cartão de Cidadão', 'CC'],
        'links': [
            'https://www.autenticacao.gov.pt/documents/20126/0/'
            'Valida%C3%A7%C3%A3o%2Bde%2BN%C3%BAmero%2Bde%2BDocumento%2Bdo%2BCart%C3%A3o%2Bde%2BCidad%C3%A3o%2B'
            '%281%29.pdf/7d5745ba-2bcc-e861-3954-bafe9f7591a0?t=1658411665319'
        ],
        'deprecated': False
    })

    @staticmethod
    def validate(id_number: str) -> bool:
        """Validate the compact format and full-card checksum, not issuance."""
        return CitizenCard.checksum(id_number)

    @staticmethod
    def checksum(id_number: str) -> bool:
        """Return whether the compact document passes the AMA full-card checksum."""
        if not validate_regexp(id_number, CitizenCard.METADATA.regexp):
            return False
        alphabet = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        values = [alphabet.index(character) for character in id_number[:-1]]
        # AMA subtracts nine exactly once from each doubled value >= 10, including letters.
        return luhn_digit(values, multipliers_start_by_two=True) == int(id_number[-1])
