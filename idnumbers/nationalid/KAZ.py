from .kaz.business_id import BusinessIDNumber
from .kaz.individual_id import IndividualIDNumber
from .kaz.util import EntityType, EntityDivision
from .util import alias_of

NationalID = alias_of(IndividualIDNumber)
"""alias of IndividualIDNumber"""
