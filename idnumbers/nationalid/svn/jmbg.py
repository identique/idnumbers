from copy import copy
from typing import Optional, Tuple
from ..constant import Citizenship
from ..yugoslavia import ParseResult, UniqueMasterCitizenNumber as YugoslaviaJMBG

SVN_METADATA = copy(YugoslaviaJMBG.METADATA)
SVN_METADATA.iso3166_alpha2 = 'SI'


class UniqueMasterCitizenNumber(YugoslaviaJMBG):
    """
    Slovenia Unique Master Citizen Number format, JMBG
    https://en.wikipedia.org/wiki/Unique_Master_Citizen_Number
    """
    METADATA = SVN_METADATA

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
        Since the Slovenia is an independent country, they share the same id code base. So, the citizenship is only for
        location in 50.
        """
        if location == '50':
            return Citizenship.CITIZEN, location
        return Citizenship.RESIDENT, location


JMBG = UniqueMasterCitizenNumber
"""
Alias of UniqueMasterCitizenNumber
"""
