"""
The idnumbers package enables your application to parse, validate against to different specs. For example, it supports
[national ID](idnumbers/nationalid.html) for parsing and validating all citizen/resident ID numbers among different
countries.

The country registry in ``idnumbers.registry`` finds the validator of a country by its ISO 3166 code.
"""

from .registry import CountryEntry as CountryEntry
from .registry import get_country as get_country
from .registry import get_validator as get_validator
from .registry import list_supported_countries as list_supported_countries
from .registry import register as register
from .registry import resolve_country as resolve_country
