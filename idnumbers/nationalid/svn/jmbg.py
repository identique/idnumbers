from copy import copy
from typing import Optional, Tuple
from ..constant import Citizenship
from ..yugoslavia import ParseResult, UniqueMasterCitizenNumber as YugoslaviaJMBG

SVN_METADATA = copy(YugoslaviaJMBG.METADATA)
SVN_METADATA.iso3166_alpha2 = 'SI'
SVN_METADATA.country_name = 'Slovenia'
SVN_METADATA.id_type = 'Unique Master Citizen Number'
SVN_METADATA.official_name = 'Enotna matična številka občana'
SVN_METADATA.display_format = 'DDMMYYYRRSSSC'
SVN_METADATA.example = '0101990500003'
SVN_METADATA.checksum_algorithm = ('Weighted sum mod 11 (digits 1-6 added to digits 7-12, weights 7, 6, 5, 4, 3, 2; '
                                   'check = 11 - remainder, 10 and 11 become 0)')
SVN_METADATA.masks = ('#############',)


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
