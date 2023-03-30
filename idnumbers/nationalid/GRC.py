from .grc.tax_id import TaxIdentityNumber
from .grc.identity_card import IdentityCard
from .grc.old_identity_card import OldIdentityCard
from .util import alias_of

NationalID = alias_of(IdentityCard)
"""
alias of IdentityCard
"""
