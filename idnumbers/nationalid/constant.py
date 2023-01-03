from enum import Enum


class Gender(Enum):
    MALE = 'male'
    FEMALE = 'female'
    NON_BINARY = 'non_binary'


class Citizenship(Enum):
    CITIZEN = 'citizen'
    RESIDENT = 'resident'
    # In some countries, foreigners are the same as resident. But in other countries, they are not the same.
    FOREIGNER = 'foreigner'
