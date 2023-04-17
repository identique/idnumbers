from types import SimpleNamespace
from .bgr.uniform_civil import UniformCivilNumber
from .bgr.unifed_id_code import UnifiedIdCode
from .util import alias_of

NationalID = alias_of(UniformCivilNumber)
"""alias of UniformCivilNumber"""
TIN = SimpleNamespace(**{
    'individual': UniformCivilNumber,
    'entity': UnifiedIdCode
})
