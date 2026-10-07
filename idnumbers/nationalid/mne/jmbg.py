from copy import copy
from typing import Optional, Tuple
from ..constant import Citizenship

from ..yugoslavia import ParseResult, UniqueMasterCitizenNumber as YugoslaviaJMBG
from ..util import alias_of

MNE_METADATA = copy(YugoslaviaJMBG.METADATA)
MNE_METADATA.iso3166_alpha2 = 'ME'
MNE_METADATA.country_name = 'Montenegro'
MNE_METADATA.id_type = 'Unique Master Citizen Number'
MNE_METADATA.official_name = 'Jedinstveni matični broj građana'
MNE_METADATA.display_format = 'DDMMYYYRRSSSC'
MNE_METADATA.example = '0101990210005'
MNE_METADATA.checksum_algorithm = ('Weighted sum mod 11 (digits 1-6 added to digits 7-12, weights 7, 6, 5, 4, 3, 2; '
                                   'check = 11 - remainder, 10 and 11 become 0)')
MNE_METADATA.masks = ('#############',)


class UniqueMasterCitizenNumber(YugoslaviaJMBG):
    """
    Montenegro Unique Master Citizen Number format, JMBG
    https://en.wikipedia.org/wiki/Unique_Master_Citizen_Number
    """
    METADATA = MNE_METADATA

    @staticmethod
    def parse(id_number: str) -> Optional[ParseResult]:
        """parse the value"""
        result = YugoslaviaJMBG.parse(id_number)
        if not result:
            return None
        loc_citizenship = UniqueMasterCitizenNumber.check_location(result['location'])
        if not loc_citizenship:
            return None
        citizenship, location = loc_citizenship
        result['citizenship'] = citizenship
        return result

    @staticmethod
    def check_location(location: str) -> Optional[Tuple[Citizenship, str]]:
        """
        Montenegro shares the JMBG code base with the other former Yugoslav republics.
        Returns (CITIZEN, location) when 20 < location < 30, (RESIDENT, location) for any other valid location,
        and None for an invalid location.
        """
        result = YugoslaviaJMBG.check_location(location)
        if not result:
            return None
        if 20 < int(location) < 30:
            return Citizenship.CITIZEN, location
        return Citizenship.RESIDENT, location


JMBG = alias_of(UniqueMasterCitizenNumber)
"""
Alias of UniqueMasterCitizenNumber
"""
