from .prt.tax_id import TaxIDNumber
from .prt.civil_id import CivilIDNumber
from .prt.citizen_card import CitizenCard
from .util import alias_of

NationalID = alias_of(CivilIDNumber)
"""alias of CivilIDNumber"""
