from .kaz.business_id import BusinessIDNumber as BusinessIDNumber
from .kaz.individual_id import IndividualIDNumber as IndividualIDNumber
from .kaz.util import EntityType as EntityType, EntityDivision as EntityDivision
from .util import alias_of

NationalID = alias_of(IndividualIDNumber)
"""alias of IndividualIDNumber"""
