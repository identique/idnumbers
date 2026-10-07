"""
The idnumbers package enables your application to parse, validate against to different specs. For example, it supports
[national ID](idnumbers/nationalid.html) for parsing and validating all citizen/resident ID numbers among different
countries.

``idnumbers.validate`` validates an ID number of any supported country in one call and says why it failed.

The country registry in ``idnumbers.registry`` finds the validator of a country by its ISO 3166 code.
"""

from .api import FailureReason as FailureReason
from .api import ParseSuccess as ParseSuccess
from .api import ParseFailure as ParseFailure
from .api import ParseIdInfoResult as ParseIdInfoResult
from .api import parse_id_info as parse_id_info
from .api import ValidationResult as ValidationResult
from .api import validate as validate
from .api import validate_many as validate_many
from .registry import CountryEntry as CountryEntry
from .registry import get_country as get_country
from .registry import get_validator as get_validator
from .registry import list_supported_countries as list_supported_countries
from .registry import register as register
from .registry import resolve_country as resolve_country
from .api import failure_reason as failure_reason
