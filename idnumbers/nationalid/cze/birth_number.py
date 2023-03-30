from copy import copy
from ..svk.birth_number import BirthNumber as SVKBirthNumber


CZE_METADATA = copy(SVKBirthNumber.METADATA)
CZE_METADATA.iso3166_alpha2 = 'CZ'
CZE_METADATA.links = ['https://en.wikipedia.org/wiki/National_identification_number#Czech_Republic_and_Slovakia']


class BirthNumber(SVKBirthNumber):
    """
    Czech Republic uses the same system of SVK. Birth Number (Czech/Slovak: rodné číslo (RČ))
    https://en.wikipedia.org/wiki/National_identification_number#Czech_Republic_and_Slovakia
    """
    METADATA = CZE_METADATA
