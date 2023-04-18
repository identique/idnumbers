from types import SimpleNamespace
from .hrv.personal_id import PersonalID
from .util import alias_of

NationalID = alias_of(PersonalID)
"""
alias of PersonalID
"""
OIB = alias_of(PersonalID)
"""
alias of PersonalID
"""
PIN = alias_of(PersonalID)
"""
alias of PersonalID
"""
TIN = SimpleNamespace(**{
    'individual': PersonalID,
    'entity': PersonalID
})
"""
According to the doc in https://www.porezna-uprava.hr/en/Pages/PIN.aspx, we know the TIN for individual and entity are
the same.
"""
