import re
from ..metadata import IdMetadata
from ..util import validate_regexp


class NationalHealthIndexNumber:
    """
    New Zealand national health index(NHI) number format
    https://techdocs.broadcom.com/us/en/symantec-security-software/information-security/data-loss-prevention/15-8/about-data-loss-prevention-policies-v27576413-d327e9/library-of-system-data-identifiers-v95989112-d327e56315/new-zealand-national-health-index-number-v117807810-d327e90250/new-zealand-national-health-index-number-narrow-br-v117808786-d327e90350.html
    Expanded-format checksum: HISO 10046:2024 section 2.1.4, Tables 1-3.
    See METADATA.links for the official standard and compliance test vectors.
    Expanded-format implementation is planned for 1 July 2027.
    Legacy implementation provenance: https://gist.github.com/mcshaz/b41dc6bd4aa3104d54da677e2b4f6b45
    """
    METADATA = IdMetadata(**{
        'iso3166_alpha2': 'NZ',
        # length without insignificant chars
        'min_length': 7,
        'max_length': 7,
        # has parse function
        'parsable': False,
        # has checksum function
        'checksum': True,
        # regular expression to validate the id
        # no I and no O in alphabet
        'regexp': re.compile(r'^('
                             r'[A-HJ-NP-Z]{3}\d{4}|'
                             r'[A-HJ-NP-Z]{3}\d{2}[A-HJ-NP-Z]{2}'
                             r')$'),
        'alias_of': None,
        'names': ['National Health Index Number',
                  'NHI'],
        'links': ['https://www.tewhatuora.govt.nz/assets/Publications/HISO-Standards/'
                  'HISO-10046-2024-Consumer-Health-Identity-Standard.pdf',
                  'https://nhi-ig.hip.digital.health.nz/ComplianceTestingImportantInformation.html',
                  'https://www.healthnz.govt.nz/health-professionals/guidance-standards/topic/'
                  'health-identity/national-health-index-nhi/upcoming-changes-to-the-nhi',
                  'https://techdocs.broadcom.com/us/en/symantec-security-software/information-security/'
                  'data-loss-prevention/15-8/about-data-loss-prevention-policies-v27576413-d327e9/'
                  'library-of-system-data-identifiers-v95989112-d327e56315/'
                  'new-zealand-national-health-index-number-v117807810-d327e90250/'
                  'new-zealand-national-health-index-number-narrow-br-v117808786-d327e90350.html'],
        'deprecated': False,
        'country_name': 'New Zealand',
        'id_type': 'National Health Index Number',
        'official_name': None,
        'display_format': 'LLL####',
        'example': 'ZZZ0016',
        'checksum_algorithm': 'Weighted sum (weights 7-2; letters A-Z without I and O count as 1-24): mod 11 for the '
                              'legacy format, mod 23 for the expanded format',
        'masks': ('LLL####', 'LLL##LL')
    })

    ALPHABET_LIST = list('ABCDEFGHJKLMNPQRSTUVWXYZ')

    @staticmethod
    def validate(id_number: str) -> bool:
        """
        Validate the NZL NHI number
        """
        return NationalHealthIndexNumber.checksum(id_number)

    @staticmethod
    def checksum(id_number: str) -> bool:
        """Validate the legacy mod-11 or expanded mod-23 checksum.

        HISO 10046:2024 section 2.1.4 maps letters A-Z (excluding I/O) to
        1-24. For the expanded format, subtract the weighted sum's remainder
        modulo 23 from 23 to obtain the 1-based check-letter index (1-23).
        """
        if not validate_regexp(id_number, NationalHealthIndexNumber.METADATA.regexp):
            return False
        check_digit = id_number[-1]
        source_list = list(id_number[:-1])
        total = 0
        for (index, char) in enumerate(source_list):
            if char in NationalHealthIndexNumber.ALPHABET_LIST:
                decimal = NationalHealthIndexNumber.ALPHABET_LIST.index(char) + 1
            else:
                decimal = int(char)
            total += decimal * (7 - index)
        if check_digit in NationalHealthIndexNumber.ALPHABET_LIST:
            # new NHI format
            modulus = total % 23
            return NationalHealthIndexNumber.ALPHABET_LIST[22 - modulus] == check_digit
        else:
            check_decimal = int(check_digit)
            # old NHI format
            modulus = total % 11
            if modulus == 0:
                return False
            return check_decimal == 0 if modulus == 1 else check_decimal == (11 - modulus)
