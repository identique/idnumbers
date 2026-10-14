from .deu.tax_id import TaxID as TaxID
from .deu.tax_number import TaxNumber as TaxNumber
from .util import alias_of

NationalID = alias_of(TaxID)
"""alias of TaxID"""
IdNr = alias_of(TaxID)
"""alias of TaxID"""
Steuernummer = alias_of(TaxNumber)
"""alias of TaxNumber"""
