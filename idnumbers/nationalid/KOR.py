from .kor.resident_registration import ResidentRegistration as ResidentRegistration
from .kor.old_registration_registration import OldResidentRegistration as OldResidentRegistration
from .kor.arc import ARC as ARC
from .util import alias_of

NationalID = alias_of(ResidentRegistration)
