from types import SimpleNamespace
from .cze.birth_number import BirthNumber
from .cze.dic import TaxNumber
from .util import alias_of

NationalID = alias_of(BirthNumber)
"""alias of BirthNumber"""

TIN = SimpleNamespace(**{
    'individual': TaxNumber,
    'entity': TaxNumber
})
