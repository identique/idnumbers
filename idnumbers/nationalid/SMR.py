from .smr.social_security import SocialSecurityNumber as SocialSecurityNumber
from .smr.tax_registration import TaxRegistrationNumber as TaxRegistrationNumber
from .util import alias_of

NationalID = alias_of(SocialSecurityNumber)
"""
alias of SocialSecurityNumber
"""
