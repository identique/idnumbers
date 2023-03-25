from typing import Union
from .lva.personal_code import PersonalCode
from .lva.old_personal_code import OldPersonalCode


def get_validator(id_number: str) -> Union[type[PersonalCode], type[OldPersonalCode]]:
    """check the first 2 char to return the correct class"""

    try:
        return PersonalCode if int(id_number[0:2]) > 31 else OldPersonalCode
    except ValueError:
        return OldPersonalCode


NationalID = PersonalCode
"""alias of PersonalCode"""
