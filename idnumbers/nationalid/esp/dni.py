import re
from types import SimpleNamespace
from ..util import validate_regexp


class DNI:
    """
    Spain National ID number
    Documento Nacional de Identidad (DNI)
    https://en.wikipedia.org/wiki/National_identification_number#Spain
    https://es.wikipedia.org/wiki/C%C3%B3digo_de_identificaci%C3%B3n_fiscal
    https://gist.github.com/afgomez/5691823

    Input normalization accepts ASCII lowercase check letters and surrounding whitespace via str.strip(),
    following python-stdnum 2.2 (not its internal separator removal):
    https://github.com/arthurdejong/python-stdnum/blob/2.2/stdnum/es/dni.py
    This is a user-input policy, not a claim that issued DNI numbers use lowercase letters.
    The unchanged mod-23 check-letter table is documented by Spain's Ministry of Interior (see METADATA.links).
    """
    METADATA = SimpleNamespace(**{
        'iso3166_alpha2': 'ES',
        # length without insignificant chars
        'min_length': 9,
        'max_length': 9,
        'parsable': False,
        'checksum': True,
        'regexp': re.compile(r'^(\d{8})([A-Za-z])$'),
        'alias_of': None,
        'names': ['Documento Nacional de Identidad',
                  'DNI'],
        'links': ['https://en.wikipedia.org/wiki/National_identification_number#Spain',
                  'https://es.wikipedia.org/wiki/C%C3%B3digo_de_identificaci%C3%B3n_fiscal',
                  'https://www.interior.gob.es/opencms/es/servicios-al-ciudadano/tramites-y-gestiones/dni/'
                  'calculo-del-digito-de-control-del-nif-nie/'],
        'deprecated': False
    })

    @staticmethod
    def validate(id_number: str) -> bool:
        """
        Validate the Spain national id number
        """
        return DNI.checksum(id_number)

    MAGIC_LETTERS = 'TRWAGMYFPDXBNJZSQVHLCKE'

    @staticmethod
    def checksum(id_number: str) -> bool:
        """algorithm: https://en.wikipedia.org/wiki/Documento_Nacional_de_Identidad_(Spain%29#Number"""
        if not isinstance(id_number, str):
            return False
        id_number = id_number.strip()
        # Guard the raw payload before uppercasing: Unicode lookalikes must not become ASCII letters.
        if not validate_regexp(id_number, DNI.METADATA.regexp):
            return False
        id_number = id_number.upper()
        idx = int(id_number[:-1]) % 23
        return DNI.MAGIC_LETTERS[idx] == id_number[-1]
