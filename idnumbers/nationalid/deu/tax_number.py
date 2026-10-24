import re
from typing import Dict, List, Optional, Tuple, TypedDict
from ..metadata import IdMetadata
from ..util import validate_regexp


class ParseResult(TypedDict):
    """Parse result of TaxNumber"""

    state: str
    """ISO 3166-2 code of the federal state, such as DE-BY"""
    tax_office: str
    """4-digit federal tax office number (Bundesfinanzamtsnummer)"""
    district: str
    """district number (Bezirksnummer): 3 digits, 4 digits in North Rhine-Westphalia"""
    distinguishing_number: str
    """distinguishing number (Unterscheidungsnummer): 4 digits, 3 digits in North Rhine-Westphalia"""
    checksum: int
    """check digit"""


# state number (Länderschlüssel), the leading digits of the federal tax office number, to ISO 3166-2 code
STATES: Dict[str, str] = {
    "10": "DE-SL",
    "11": "DE-BE",
    "21": "DE-SH",
    "22": "DE-HH",
    "23": "DE-NI",
    "24": "DE-HB",
    "26": "DE-HE",
    "27": "DE-RP",
    "28": "DE-BW",
    "30": "DE-BB",
    "31": "DE-ST",
    "32": "DE-SN",
    "40": "DE-MV",
    "41": "DE-TH",
    "5": "DE-NW",
    "9": "DE-BY",
}

# states of the Bavarian programming group, whose district number is at least 100
BAVARIAN_GROUP = {"DE-BY", "DE-BB", "DE-MV", "DE-SL", "DE-SN", "DE-ST", "DE-TH"}

# weights of the 11er-Verfahren over the first 12 digits of the ELSTER format
WEIGHTS_BAVARIA = [0, 5, 4, 3, 0, 2, 7, 6, 5, 4, 3, 2]
WEIGHTS_BREMEN = [0, 0, 4, 3, 0, 2, 7, 6, 5, 4, 3, 2]
WEIGHTS_LOWER_SAXONY = [0, 0, 2, 9, 0, 8, 7, 6, 5, 4, 3, 2]
WEIGHTS_BERLIN_A = [0, 0, 0, 0, 0, 7, 6, 5, 8, 4, 3, 2]
WEIGHTS_BERLIN_B = [0, 0, 2, 9, 0, 8, 7, 6, 5, 4, 3, 2]
WEIGHTS_NRW = [0, 3, 2, 1, 0, 7, 6, 5, 4, 3, 2, 1]
WEIGHTS_11 = {
    "DE-BY": WEIGHTS_BAVARIA,
    "DE-BB": WEIGHTS_BAVARIA,
    "DE-MV": WEIGHTS_BAVARIA,
    "DE-SL": WEIGHTS_BAVARIA,
    "DE-SN": WEIGHTS_BAVARIA,
    "DE-ST": WEIGHTS_BAVARIA,
    "DE-TH": WEIGHTS_BAVARIA,
    "DE-HB": WEIGHTS_BREMEN,
    "DE-HH": WEIGHTS_BREMEN,
    "DE-NI": WEIGHTS_LOWER_SAXONY,
}

# summands and factors of the 2er-Verfahren over the first 12 digits of the ELSTER format
SUMMANDS_2 = [0, 0, 9, 8, 0, 7, 6, 5, 4, 3, 2, 1]
FACTORS_2 = [0, 0, 512, 256, 0, 128, 64, 32, 16, 8, 4, 2]
STATES_2 = {"DE-BW", "DE-HE", "DE-SH"}

# factors of the modified 11er-Verfahren (Rhineland-Palatinate) over the first 12 digits of the ELSTER format
FACTORS_RP = [0, 0, 1, 2, 0, 1, 2, 1, 2, 1, 2, 1]

# Berlin tax offices that use Berlin-A, with the district ranges (inclusive) that use Berlin-B instead
BERLIN_A: Dict[str, List[Tuple[int, int]]] = {
    "1113": [(201, 693)],
    "1114": [(201, 693)],
    "1116": [(1, 29), (201, 693), (875, 899)],
    "1117": [(201, 693)],
    "1119": [(201, 639), (680, 680), (684, 684)],
    "1120": [(201, 693)],
    "1121": [(201, 693)],
    "1123": [(201, 693)],
    "1124": [(201, 693)],
    "1125": [(201, 693)],
    "1127": [],
    "1129": [],
    "1130": [],
}
# Berlin tax offices that always use Berlin-B
BERLIN_B = {
    "1115",
    "1118",
    "1131",
    "1132",
    "1133",
    "1134",
    "1135",
    "1136",
    "1137",
    "1138",
    "1194",
    "1195",
    "1196",
    "1197",
    "1198",
}


def get_state(id_number: str) -> str:
    """the ISO 3166-2 code of the federal state of a number that matches TaxNumber.METADATA.regexp"""
    return STATES.get(id_number[:1]) or STATES[id_number[:2]]


def eleven_digit(numbers: List[int], weights: List[int]) -> Optional[int]:
    """11er-Verfahren: the difference of the weighted sum to the next multiple of 11, None if it has two digits"""
    check = -sum(number * weight for number, weight in zip(numbers, weights)) % 11
    return None if check == 10 else check


def nrw_digit(numbers: List[int]) -> Optional[int]:
    """
    11er-Verfahren of North Rhine-Westphalia: the weighted sum modulo 11, None if it has two digits

    ELSTER section 6.6 does not state the case of remainder 0 for North Rhine-Westphalia; a check digit of 0 is
    inferred from the rule that the remainder is the check digit.
    """
    check = sum(number * weight for number, weight in zip(numbers, WEIGHTS_NRW)) % 11
    return None if check == 10 else check


def two_digit(numbers: List[int]) -> int:
    """2er-Verfahren"""
    total = 0
    for number, summand, factor in zip(numbers, SUMMANDS_2, FACTORS_2):
        if factor == 0:
            continue
        product = (number + summand) % 10 * factor
        while product > 9:
            product = sum(int(char) for char in str(product))
        total += product
    return -total % 10


def rp_digit(numbers: List[int]) -> int:
    """
    modified 11er-Verfahren of Rhineland-Palatinate

    ELSTER section 6.4 does not state the case of a sum that ends in 0; a check digit of 0 is inferred, as the 2er- and
    11er-Verfahren state it for their own sums.
    """
    total = 0
    for number, factor in zip(numbers, FACTORS_RP):
        product = number * factor
        total += product % 10 + 1 if product > 9 else product
    return -total % 10


def berlin_weights(tax_office: str, district: int) -> List[int]:
    """the Berlin weights of a tax office listed in ELSTER section 7.2 (the regexp rejects unlisted offices)"""
    if tax_office in BERLIN_A and not any(low <= district <= high for low, high in BERLIN_A[tax_office]):
        return WEIGHTS_BERLIN_A
    return WEIGHTS_BERLIN_B


class TaxNumber:
    """
    Germany tax number, Steuernummer, St.-Nr., in the 13-digit ELSTER format

    The tax offices of the federal states allocate the tax number. The ELSTER format is FFFF0BBBUUUUP, and FFFF0BBBBUUUP
    in North Rhine-Westphalia (display format FFFF0BBB{BU}UUUC covers both): the 4-digit federal tax office number
    (Bundesfinanzamtsnummer), whose leading digits are the state number, a 0, the district number (Bezirksnummer), the
    distinguishing number (Unterscheidungsnummer) and the check digit.

    The rules follow chapters 3 to 7 of the ELSTER document "Prüfung der Steuer- und Steueridentifikationsnummer"
    (Bayerisches Landesamt für Steuern):
    https://download.elster.de/download/schnittstellen/Pruefung_der_Steuer_und_Steueridentifikatsnummer.pdf

    - The state number is one of the 16 federal states, and the 5th digit is 0.
    - The district number is not 000, 998 or 999 (0000, 0998 or 0999 in North Rhine-Westphalia), and it is at least
      100 in the states of the Bavarian programming group (Bavaria, Brandenburg, Mecklenburg-Western Pomerania,
      Saarland, Saxony, Saxony-Anhalt and Thuringia).
    - In North Rhine-Westphalia, the distinguishing number and the check digit together are greater than 0009.
    - The check digit follows the method of the state: the 2er-Verfahren in Baden-Württemberg, Hesse and
      Schleswig-Holstein, the modified 11er-Verfahren in Rhineland-Palatinate, and the 11er-Verfahren with
      state-specific weights elsewhere. Berlin uses the weights Berlin-A or Berlin-B by tax office and district, as
      listed in section 7.2; a Berlin tax office missing from that table is rejected, because its method is unknown.
      Numbers whose check digit would have two digits are never allocated.

    Only the ELSTER format is accepted. The format printed on tax notices (for example 198/815/08152) omits part of
    the federal tax office number, so it can't be validated reliably. The tax office itself is not checked against
    the list of offices, which ELSTER publishes separately and changes over time.
    """

    METADATA = IdMetadata(
        **{
            "iso3166_alpha2": "DE",
            "min_length": 13,
            "max_length": 13,
            "parsable": True,
            "checksum": True,
            # state number and tax office: Berlin (11) is limited to the offices listed in ELSTER section 7.2
            "regexp": re.compile(
                r"^(?:(?:10|2[1-46-8]|3[0-2]|4[01]|5\d|9\d)\d{2}|11(?:1[3-9]|2[0134579]|3[0-8]|9[4-8]))0\d{8}$"
            ),
            "alias_of": None,
            "names": ["Tax Number", "Steuernummer", "St.-Nr."],
            "links": [
                "https://download.elster.de/download/schnittstellen/Pruefung_der_Steuer_und_Steueridentifikatsnummer.pdf",
            ],
            "deprecated": False,
            "country_name": "Germany",
            "id_type": "Tax Number",
            "official_name": "Steuernummer",
            "display_format": "FFFF0BBB{BU}UUUC",
            "example": "9198081508152",
            "checksum_algorithm": "State-specific: 11er-Verfahren (weighted mod 11), 2er-Verfahren or modified "
            "11er-Verfahren (Rhineland-Palatinate)",
            "masks": ("#############",),
        }
    )

    @staticmethod
    def validate(id_number: str) -> bool:
        """
        Validate the DEU tax number in the ELSTER format
        """
        return TaxNumber.parse(id_number) is not None

    @staticmethod
    def parse(id_number: str) -> Optional[ParseResult]:
        """Parse the DEU tax number in the ELSTER format, None if it is invalid"""
        if not validate_regexp(id_number, TaxNumber.METADATA.regexp):
            return None
        state = get_state(id_number)
        if state == "DE-NW":
            district, distinguishing_number = id_number[5:9], id_number[9:12]
            if int(id_number[9:13]) <= 9:
                return None
        else:
            district, distinguishing_number = id_number[5:8], id_number[8:12]
        if int(district) in (0, 998, 999):
            return None
        if state in BAVARIAN_GROUP and int(district) < 100:
            return None
        if not TaxNumber.checksum(id_number):
            return None
        return {
            "state": state,
            "tax_office": id_number[:4],
            "district": district,
            "distinguishing_number": distinguishing_number,
            "checksum": int(id_number[12]),
        }

    @staticmethod
    def checksum(id_number: str) -> bool:
        """Validate the check digit, False when the input is not a well-formed tax number"""
        if not validate_regexp(id_number, TaxNumber.METADATA.regexp):
            return False
        state = get_state(id_number)
        numbers = [int(char) for char in id_number]
        check = numbers[12]
        if state == "DE-NW":
            return nrw_digit(numbers[:12]) == check
        if state in STATES_2:
            return two_digit(numbers[:12]) == check
        if state == "DE-RP":
            return rp_digit(numbers[:12]) == check
        if state == "DE-BE":
            weights = berlin_weights(id_number[:4], int(id_number[5:8]))
        else:
            weights = WEIGHTS_11[state]
        return eleven_digit(numbers[:12], weights) == check
