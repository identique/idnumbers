from .ukr.entity_id import EntityIDNumber
from .ukr.taxpayer_id import TaxpayerIDNumber
from .util import alias_of

NationalID = alias_of(TaxpayerIDNumber)
"""alias of TaxpayerIDNumber"""
