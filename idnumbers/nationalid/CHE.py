from .che.social_security import SocialSecurityNumber
from .che.business_id import BusinessID
from .util import alias_of

AVH = alias_of(SocialSecurityNumber)
"""alias of SocialSecurityNumber"""
NationalID = alias_of(SocialSecurityNumber)
"""alias of SocialSecurityNumber"""

UID = alias_of(BusinessID)
"""alias of Business ID"""
