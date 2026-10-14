from types import SimpleNamespace
from .lux.national_id import NationalID as NationalID
from .lux.entity_tin import EntityTIN as EntityTIN

TIN = SimpleNamespace(**{"individual": NationalID, "entity": EntityTIN})
"""
According to the OECD TIN sheet for Luxembourg, the 13-digit national identification number is the TIN of a natural
person, and the 11-digit national identifier is the TIN of a non-natural person.
https://www.oecd.org/tax/automatic-exchange/crs-implementation-and-assistance/tax-identification-numbers/Luxembourg-TIN.pdf
"""
