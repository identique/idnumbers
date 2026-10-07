from .prt.tax_id import TaxIDNumber as TaxIDNumber
from .prt.civil_id import CivilIDNumber as CivilIDNumber
from .prt.citizen_card import CitizenCard as CitizenCard
from .util import alias_of

NationalID = alias_of(CivilIDNumber)
"""alias of CivilIDNumber"""
