from types import SimpleNamespace
from .aut.entity_tax_id import EntityTaxIDNumber as EntityTaxIDNumber
from .aut.tax_id import TaxIDNumber as TaxIDNumber
from .util import alias_of

NationalID = alias_of(TaxIDNumber)
"""alias of TaxIDNumber"""

TIN = SimpleNamespace(**{
    'individual': TaxIDNumber,
    'entity': EntityTaxIDNumber
})
