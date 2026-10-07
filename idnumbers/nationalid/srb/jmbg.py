from copy import copy
from typing import Optional, Tuple
from ..constant import Citizenship

from ..yugoslavia import ParseResult, UniqueMasterCitizenNumber as YugoslaviaJMBG
from ..util import alias_of

SRB_METADATA = copy(YugoslaviaJMBG.METADATA)
SRB_METADATA.iso3166_alpha2 = 'RS'
SRB_METADATA.country_name = 'Serbia'
SRB_METADATA.id_type = 'Unique Master Citizen Number'
SRB_METADATA.official_name = 'Јединствени матични број грађана'
SRB_METADATA.display_format = 'DDMMYYYRRSSSC'
SRB_METADATA.example = '0101990700002'
SRB_METADATA.checksum_algorithm = ('Weighted sum mod 11 (digits 1-6 added to digits 7-12, weights 7, 6, 5, 4, 3, 2; '
                                   'check = 11 - remainder, 10 and 11 become 0)')
SRB_METADATA.masks = ('#############',)


class UniqueMasterCitizenNumber(YugoslaviaJMBG):
    """
    Serbia Unique Master Citizen Number format, JMBG
    https://en.wikipedia.org/wiki/Unique_Master_Citizen_Number
    """
    METADATA = SRB_METADATA

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
        Serbia shares the JMBG code base with the other former Yugoslav republics.
        Returns (CITIZEN, location) when location > 70, (RESIDENT, location) for any other valid location,
        and None for an invalid location.
        """
        result = YugoslaviaJMBG.check_location(location)
        if not result:
            return None
        if int(location) > 70:
            return Citizenship.CITIZEN, location
        return Citizenship.RESIDENT, location


JMBG = alias_of(UniqueMasterCitizenNumber)
"""
Alias of UniqueMasterCitizenNumber
"""
