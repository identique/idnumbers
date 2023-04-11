from types import SimpleNamespace
from .bel.national_registration import NationalRegistrationNumber
from .bel.entity_vat import EntityVAT
from .util import alias_of

NationalID = alias_of(NationalRegistrationNumber)
"""alias of national registration number"""

TIN = SimpleNamespace(**{
    'individual': NationalRegistrationNumber,
    'entity': EntityVAT
})
