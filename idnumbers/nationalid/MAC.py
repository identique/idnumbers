from .mac.national_id import NationalID as NationalID, DocType as DocType
from .mac.arc import ARC as ARC
from .util import alias_of

BIRP = alias_of(NationalID)
BIRNP = alias_of(NationalID)
"""alias of NationalID"""
