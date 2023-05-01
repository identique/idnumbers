from types import SimpleNamespace
from .cyp.tax_number import TaxNumber
from .util import alias_of

NationalID = alias_of(TaxNumber)
"""alias of tax number (to find a better one)"""

TIN = SimpleNamespace(**{
    'individual': TaxNumber,
    'entity': TaxNumber
})
