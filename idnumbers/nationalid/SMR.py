from .smr.social_security import SocialSecurityNumber
from .smr.tax_registration import TaxRegistrationNumber
from .util import alias_of

NationalID = alias_of(SocialSecurityNumber)
"""
alias of SocialSecurityNumber
"""
