from types import SimpleNamespace

from .grc.tax_id import TaxIdentityNumber as TaxIdentityNumber
from .grc.identity_card import IdentityCard as IdentityCard
from .grc.old_identity_card import OldIdentityCard as OldIdentityCard
from .util import alias_of

NationalID = alias_of(IdentityCard)
"""
alias of IdentityCard
"""
TIN = SimpleNamespace(**{"individual": TaxIdentityNumber, "entity": TaxIdentityNumber})
"""
The OECD Greece TIN sheet lists a TIN for natural and legal persons; both fields expose the existing AFM class:
https://www.oecd.org/content/dam/oecd/en/topics/policy-issue-focus/aeoi/greece-tin.pdf
"""
