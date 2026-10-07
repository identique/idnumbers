from copy import copy
from typing import Optional, Tuple
from ..constant import Citizenship

from ..yugoslavia import ParseResult, UniqueMasterCitizenNumber as YugoslaviaJMBG
from ..util import alias_of

MKD_METADATA = copy(YugoslaviaJMBG.METADATA)
MKD_METADATA.iso3166_alpha2 = 'MK'


class UniqueMasterCitizenNumber(YugoslaviaJMBG):
    """
    North Macedonia Unique Master Citizen Number format, JMBG
    https://en.wikipedia.org/wiki/Unique_Master_Citizen_Number
    """
    METADATA = MKD_METADATA

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
        North Macedonia shares the JMBG code base with the other former Yugoslav republics.
        Returns (CITIZEN, location) when 40 < location < 50, (RESIDENT, location) for any other valid location,
        and None for an invalid location.
        """
        result = YugoslaviaJMBG.check_location(location)
        if not result:
            return None
        if 40 < int(location) < 50:
            return Citizenship.CITIZEN, location
        return Citizenship.RESIDENT, location


JMBG = alias_of(UniqueMasterCitizenNumber)
"""
Alias of UniqueMasterCitizenNumber
"""
