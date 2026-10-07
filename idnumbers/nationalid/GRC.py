from .grc.tax_id import TaxIdentityNumber as TaxIdentityNumber
from .grc.identity_card import IdentityCard as IdentityCard
from .grc.old_identity_card import OldIdentityCard as OldIdentityCard
from .util import alias_of

NationalID = alias_of(IdentityCard)
"""
alias of IdentityCard
"""
