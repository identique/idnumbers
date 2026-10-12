import re
from ..metadata import IdMetadata
from ..util import validate_regexp
from .util import normalize


class RGNumber:
    """
    Brazil Registro Geral Number

    This library uses weights 2 through 9 over the first eight digits and the complement of their sum modulo 11:
    remainder 0 gives 0, and remainder 1 gives X (value 10). This is the library's chosen convention, not a claim
    about every state's RG issuance rules. The sources below describe generic modulo-11 arithmetic: SBMAC uses
    X for 10, and UFSC discusses alternative mappings for remainders 0 and 1.

    https://proceedings.sbmac.org.br/sbmac/article/viewFile/1695/1703
    https://legado.moodle.ufsc.br/pluginfile.php/6080117/mod_resource/content/2/digito_verificador.pdf
    https://en.wikipedia.org/wiki/National_identification_number#Brazil
    https://en.wikipedia.org/wiki/Brazilian_identity_card
    """

    METADATA = IdMetadata(
        **{
            "iso3166_alpha2": "BR",
            # length without insignificant chars
            "min_length": 9,
            "max_length": 9,
            "parsable": False,
            "checksum": True,
            "regexp": re.compile(r"^(\d{2}\.\d{3}\.\d{3}-[\dX])$"),
            "alias_of": None,
            "names": ["RG number", "Registro Geral number"],
            "links": [
                "https://en.wikipedia.org/wiki/National_identification_number#Brazil",
                "https://en.wikipedia.org/wiki/Brazilian_identity_cards",
                "https://proceedings.sbmac.org.br/sbmac/article/viewFile/1695/1703",
                "https://legado.moodle.ufsc.br/pluginfile.php/6080117/mod_resource/content/2/digito_verificador.pdf",
            ],
            "deprecated": False,
            "country_name": "Brazil",
            "id_type": "General Registry Number",
            "official_name": "Registro Geral",
            "display_format": "##.###.###-X",
            "example": "12.345.678-2",
            "checksum_algorithm": "Library convention: weights 2-9 over the first eight digits; check value is the "
            "complement of the sum modulo 11 (remainder 0 gives 0, remainder 1 gives X; X counts as 10)",
            "masks": ("##.###.###-X",),
        }
    )

    @staticmethod
    def validate(id_number: str) -> bool:
        """
        Validate the BRA Registro Geral Number
        """
        if not validate_regexp(id_number, RGNumber.METADATA.regexp):
            return False
        return RGNumber.checksum(id_number)

    MULTIPLIER = [2, 3, 4, 5, 6, 7, 8, 9]

    @staticmethod
    def checksum(id_number: str) -> bool:
        """Validate RG number checksum, False when the input is not a well-formed RG number"""
        if not validate_regexp(id_number, RGNumber.METADATA.regexp):
            return False
        normalized = normalize(id_number)
        number_list = [int(char) for char in list(normalized[:8])]
        # X represents check value 10; the check weight 100 is congruent to 1 modulo 11.
        if normalized[8] == "X":
            check_digit = 10
        else:
            check_digit = int(normalized[8])
        total = sum([value * RGNumber.MULTIPLIER[index] for (index, value) in enumerate(number_list)])
        return True if ((total + check_digit * 100) % 11) == 0 else False
