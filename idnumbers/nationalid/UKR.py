from .ukr.entity_id import EntityIDNumber as EntityIDNumber
from .ukr.taxpayer_id import TaxpayerIDNumber as TaxpayerIDNumber
from .util import alias_of

NationalID = alias_of(TaxpayerIDNumber)
"""alias of TaxpayerIDNumber"""
