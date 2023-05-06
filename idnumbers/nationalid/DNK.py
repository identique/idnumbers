from types import SimpleNamespace
from .dnk.personal_id import PersonalIdentityNumber
from .dnk.entity_vat import EntityVAT
from .util import alias_of

NationalID = alias_of(PersonalIdentityNumber)
"""alias of PersonalIdentityNumber"""
CPR = alias_of(PersonalIdentityNumber)
"""alias of PersonalIdentityNumber"""

TIN = SimpleNamespace(**{
    'individual': PersonalIdentityNumber,
    'entity': EntityVAT
})
