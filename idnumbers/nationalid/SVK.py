from .svk.birth_number import BirthNumber as BirthNumber
from .svk.citizen_id import CitizenIDNumber as CitizenIDNumber
from .util import alias_of

NationalID = alias_of(BirthNumber)
"""alias of BirthNumber"""
