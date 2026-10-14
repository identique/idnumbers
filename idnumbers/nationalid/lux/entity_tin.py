import re
from ..metadata import IdMetadata
from ..util import validate_regexp, weighted_modulus_digit


class EntityTIN:
    """
    Luxembourg TIN-like number for non-natural persons (entities)

    The national identifier of a non-natural person, regulated by the law of 30 March 1979, is used as its TIN. It has
    11 digits and the last one is a check digit. Multiply the first ten digits by the weights 5, 4, 3, 2, 7, 6, 5, 4, 3
    and 2 and take the remainder of the sum divided by 11. The check digit is 11 minus that remainder, and 0 when the
    remainder is 0. A remainder of 1 is never allocated, so such numbers are invalid.

    Only the check digit is verified: the OECD sheet does not describe the meaning of the first ten digits.

    https://www.oecd.org/tax/automatic-exchange/crs-implementation-and-assistance/tax-identification-numbers/Luxembourg-TIN.pdf
    """

    METADATA = IdMetadata(
        **{
            "iso3166_alpha2": "LU",
            "min_length": 11,
            "max_length": 11,
            "parsable": False,
            "checksum": True,
            "regexp": re.compile(r"^\d{11}$"),
            "alias_of": None,
            "names": ["Entity TIN", "TIN for non-natural persons", "National identifier of non-natural persons"],
            "links": [
                "https://www.oecd.org/tax/automatic-exchange/crs-implementation-and-assistance/"
                "tax-identification-numbers/Luxembourg-TIN.pdf",
                "https://impotsdirects.public.lu/fr/az/n/num__ro_dossier.html",
            ],
            "deprecated": False,
            "country_name": "Luxembourg",
            "id_type": "Tax Identification Number for Entities",
            "official_name": None,
            "display_format": "###########",
            "example": "12345678903",
            "checksum_algorithm": "Weighted mod 11 check digit (weights 5, 4, 3, 2, 7, 6, 5, 4, 3, 2): 11 minus the "
            "remainder, 0 for remainder 0; remainder 1 is never allocated",
            "masks": ("###########",),
        }
    )

    MULTIPLIER = [5, 4, 3, 2, 7, 6, 5, 4, 3, 2]

    @staticmethod
    def validate(id_number: str) -> bool:
        """
        Validate the LUX TIN of a non-natural person
        """
        if not validate_regexp(id_number, EntityTIN.METADATA.regexp):
            return False
        return EntityTIN.checksum(id_number)

    @staticmethod
    def checksum(id_number: str) -> bool:
        """Validate the check digit, False when the input is not a well-formed entity TIN"""
        if not validate_regexp(id_number, EntityTIN.METADATA.regexp):
            return False
        numbers = [int(char) for char in id_number]
        remainder = weighted_modulus_digit(numbers[:10], EntityTIN.MULTIPLIER, 11, True)
        if remainder == 1:
            # a remainder of 1 is not allocated
            return False
        check_digit = 0 if remainder == 0 else 11 - remainder
        return numbers[10] == check_digit
