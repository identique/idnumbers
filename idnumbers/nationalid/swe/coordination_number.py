import re
from ..metadata import IdMetadata
from typing import Optional
from .personal_id import ParseResult, _checksum, _parse


class CoordinationNumber:
    """
    Sweden coordination number (samordningsnummer).

    Uses the same serial, gender and checksum rules as personnummer, with 60 added to the
    birth day. The checksum uses the encoded day; parsing returns the decoded calendar date.
    Accepts 10 or 12 digits and an optional ``-`` or ``+`` before the last four digits.
    Explicit years determine the century; two-digit years follow personnummer decoding.
    Validation checks syntax, calendar date and checksum, not issuance or active identity status.

    `Skatteverket guidance`_ describes the encoded day and serial/checksum rules.
    The twelve-digit system format is also documented in the API specification linked in metadata.

    .. _Skatteverket guidance:
        https://www.skatteverket.se/offentligaaktorer/folkbokforing/
        samordningsnummerforoffentligaaktorer.4.46ae6b26141980f1e2d3643.html
    """
    METADATA = IdMetadata(**{
        'iso3166_alpha2': 'SE',
        # length without insignificant chars
        'min_length': 10,
        'max_length': 12,
        'parsable': True,
        'checksum': True,
        'regexp': re.compile(r'^(?P<century>[0-9]{2})?(?P<yy>[0-9]{2})(?P<mm>[0-9]{2})'
                             r'(?P<dd>6[1-9]|[78][0-9]|9[01])(?P<sep>[+-])?'
                             r'(?!000)(?P<birth_number>[0-9]{3})(?P<checksum>[0-9])$'),
        'alias_of': None,
        'names': ['Coordination Number', 'samordningsnummer'],
        'links': ['https://www.skatteverket.se/offentligaaktorer/folkbokforing/'
                  'samordningsnummerforoffentligaaktorer.4.46ae6b26141980f1e2d3643.html',
                  'https://www.skatteverket.se/offentligaaktorer/folkbokforing/'
                  'underrattaomfelaktigauppgifterforpersonermedsamordningsnummer.4.7d2cc99c18b24bd07c394b0.html',
                  'https://www7.skatteverket.se/portal-wapi/open/apier-och-oppna-data/utvecklarportalen/v1/getFile/'
                  'tjanstebeskrivning-skatteregistera-utomlands-bosatta-v1-1-2/pdf/1.0.9/'
                  'skatteregistrera-utomlands-bosatta-v1.pdf'],
        'deprecated': False,
        'country_name': 'Sweden',
        'id_type': 'Coordination Number',
        'official_name': 'samordningsnummer',
        'display_format': 'YYMMDD-SSSC',
        'example': '811278-9873',
        'checksum_algorithm': 'Luhn (mod 10) over the last ten digits, with 60 added to the day',
        'masks': ('######-####', '########-####')
    })

    @staticmethod
    def validate(id_number: str) -> bool:
        """Validate the coordination number's syntax, calendar date and checksum."""
        return CoordinationNumber.parse(id_number) is not None

    @staticmethod
    def parse(id_number: str) -> Optional[ParseResult]:
        """Parse the decoded birth date, gender and supplied checksum digit."""
        return _parse(id_number, CoordinationNumber.METADATA.regexp, day_offset=60)

    @staticmethod
    def checksum(id_number: str) -> Optional[int]:
        """Calculate Luhn from the encoded last ten digits, without checking the calendar date."""
        return _checksum(id_number, CoordinationNumber.METADATA.regexp)
