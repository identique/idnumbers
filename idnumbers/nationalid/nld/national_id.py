import re
from ..metadata import IdMetadata
from ..util import validate_regexp


def normalize(id_number: str) -> str:
    """strip out useless characters/whitespaces"""
    return re.sub(r'\.', '', id_number)


class BSN:
    """
    Netherlands National ID number
    Burgerservicenummer (BSN) (Citizen Service Number)

    Accepts nine ASCII digits, with the existing 4.2.3 dotted layout retained for compatibility.
    RvIG documents nine-digit BSNs; Logisch Ontwerp BSN 2024.Q1 describes number generation
    on page 12 and the 11-proof on page 31, footnote 22.
    https://www.rvig.nl/veelgestelde-vragen-burgerservicenummer-bsn
    https://www.rvig.nl/sites/default/files/2023-12/Logisch%20Ontwerp%20BSN%202024.Q1.pdf
    https://en.wikipedia.org/wiki/National_identification_number#Netherlands
    https://nl.wikipedia.org/wiki/Burgerservicenummer
    """
    METADATA = IdMetadata(**{
        'iso3166_alpha2': 'NL',
        # length without insignificant chars
        'min_length': 9,
        'max_length': 9,
        'parsable': False,
        'checksum': True,
        'regexp': re.compile(r'^(?!0{4}\.?0{2}\.?0{3}$)(?:[0-9]{9}|[0-9]{4}\.[0-9]{2}\.[0-9]{3})$'),
        'alias_of': None,
        'names': ['Burgerservicenummer',
                  'BSN',
                  'Citizen Service Number',
                  'Personal Number'],
        'links': ['https://en.wikipedia.org/wiki/National_identification_number#Netherlands',
                  'https://nl.wikipedia.org/wiki/Burgerservicenummer',
                  'https://www.rvig.nl/veelgestelde-vragen-burgerservicenummer-bsn',
                  'https://www.rvig.nl/sites/default/files/2023-12/Logisch%20Ontwerp%20BSN%202024.Q1.pdf'],
        'deprecated': False

    })

    @staticmethod
    def validate(id_number: str) -> bool:
        """
        Validate the BSN id number
        """
        if not validate_regexp(id_number, BSN.METADATA.regexp):
            return False
        return BSN.checksum(id_number)

    MAGIC_MULTIPLIER = [9, 8, 7, 6, 5, 4, 3, 2]

    @staticmethod
    def checksum(id_number: str) -> bool:
        """algorithm: https://nl.wikipedia.org/wiki/Burgerservicenummer#11-proef"""
        normalized = normalize(id_number)
        number_list = [int(char) for char in list(normalized[:-1])]
        total = sum([value * BSN.MAGIC_MULTIPLIER[index] for (index, value) in enumerate(number_list)])
        checksum = total % 11
        return str(total % 11) == normalized[-1] if checksum != 10 else False
