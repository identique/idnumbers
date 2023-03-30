from typing import Union
from .lva.personal_code import PersonalCode
from .lva.old_personal_code import OldPersonalCode
from .util import alias_of


def get_validator(id_number: str) -> Union[type[PersonalCode], type[OldPersonalCode]]:
    """check the first 2 char to return the correct class"""

    try:
        return PersonalCode if int(id_number[0:2]) > 31 else OldPersonalCode
    except ValueError:
        return OldPersonalCode


NationalID = alias_of(PersonalCode)
"""alias of PersonalCode"""
