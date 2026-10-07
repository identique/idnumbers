"""
The typed ``METADATA`` object of an ID class.

Every ID class has a class attribute ``METADATA``. It is an :class:`IdMetadata`, a subclass of
``types.SimpleNamespace``, so the access that predates the typed class keeps working: attribute access,
``vars()``, ``copy.copy()`` and ``getattr(metadata, 'name', default)``. The annotations only add what a type checker
and the documentation need.
"""

from re import Pattern
from types import SimpleNamespace
from typing import Any, List, Optional, Tuple, Type

__all__ = ['IdMetadata']


class IdMetadata(SimpleNamespace):
    """
    The description of one ID class.

    It is a ``types.SimpleNamespace`` with annotated fields, built from keyword arguments such as
    ``IdMetadata(**{'iso3166_alpha2': 'TW', ...})``. ``isinstance(metadata, SimpleNamespace)`` stays true.
    """

    iso3166_alpha2: str
    """The ISO 3166-1 alpha-2 code of the issuing country, such as ``'TW'``."""

    min_length: int
    """The minimum length of the ID in its compact form, that is without separators."""

    max_length: int
    """The maximum length of the ID in its compact form, that is without separators."""

    parsable: bool
    """Whether information can be parsed from the ID. If it is true, the class has a ``parse`` function."""

    checksum: bool
    """Whether the design of the ID has a check digit or check letter. If it is true, the class has a ``checksum``
    function."""

    regexp: Pattern[str]
    """The compiled pattern that describes the whole ID."""

    alias_of: Optional[Type[Any]]
    """The class this class is an alias of, or ``None`` if it is not an alias."""

    names: List[str]
    """The names and abbreviations under which the ID is known."""

    links: List[str]
    """The reference links of the ID, such as the official page or the description of the algorithm."""

    deprecated: bool
    """Whether the country has replaced the ID with a newer format."""

    country_name: str
    """The English name of the issuing country, the same as in the country registry, such as ``'Taiwan'``."""

    id_type: str
    """The English name of the kind of ID, such as ``'National Identification Card'``."""

    official_name: Optional[str]
    """The official name of the ID in the local language, such as ``'國民身分證統一編號'``. It is ``None`` when the ID
    has no local-language name, as with an ID that is named in English."""

    display_format: str
    """A human-readable layout of the ID, such as ``'###-##-####'`` or ``'YYMMDD-SSSC'``."""

    example: str
    """A synthetic ID that the class validates. It is constructed with a valid check digit and is not the number of
    any real person."""

    checksum_algorithm: Optional[str]
    """A short description of the algorithm that ``checksum`` computes, such as ``'Luhn (mod 10)'``. It is ``None``
    when ``checksum`` is false."""

    masks: Tuple[str, ...]
    """The layouts the class accepts, the preferred display layout first. ``#`` is a digit, ``L`` a letter, ``X`` a
    letter or a digit and ``*`` any non-space character. Every other character is a separator, one of
    ``' -./()'``."""
