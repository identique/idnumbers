from enum import Enum


class Gender(Enum):
    """general gender enum"""
    MALE = 'male'
    FEMALE = 'female'
    NON_BINARY = 'non_binary'
    """not all countries have this gender type."""


class Citizenship(Enum):
    CITIZEN = 'citizen'
    RESIDENT = 'resident'
