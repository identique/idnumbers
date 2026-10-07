"""Primary-ID normalization, display formatting and UI input masks.

These helpers use the registry's ``NationalID`` metadata, never its validator.
Formatting is length-only; a mask pattern describes layout, not ID validity.
Letters and digits in patterns are intentionally ASCII, even where a country
validator accepts more (for example Greek identity-card letters).
"""

import re
from dataclasses import dataclass
from typing import Any, Optional, Pattern, Tuple

from .registry import get_validator, resolve_country

__all__ = ['InputMask', 'normalize_id', 'format_id', 'get_input_mask']

_TOKENS = {'#': '[0-9]', 'L': '[A-Z]', 'X': '[A-Z0-9]', '*': r'\S'}
_WHITESPACE = re.compile(r'[\s\u200b-\u200d\u2060\ufeff]')
_SEPARATORS = re.compile(r'[\s\u200b-\u200d\u2060\ufeff.\-/()]')


@dataclass(frozen=True)
class InputMask:
    """Immutable primary-ID layouts and their case-sensitive whole-input pattern."""

    country_code: str
    """Resolved alpha-3 registry code."""
    masks: Tuple[str, ...]
    """Metadata masks: ``#`` digit, ``L`` letter, ``X`` alphanumeric, ``*`` non-space."""
    pattern: Pattern[str]
    """Compiled layout alternatives, with ASCII letters/digits and Unicode-aware non-space slots."""


def _metadata_for(country: str) -> Any:
    validator = get_validator(country)
    return None if validator is None else validator.METADATA


def _masks(metadata: Any) -> Tuple[str, ...]:
    return tuple(getattr(metadata, 'masks', ()) or ())


def _slots(mask: str) -> int:
    return sum(char in _TOKENS for char in mask)


def _fits_length(value: str, metadata: Any) -> bool:
    masks = _masks(metadata)
    if masks:
        return any(_slots(mask) == len(value) for mask in masks)
    minimum = getattr(metadata, 'min_length', None)
    maximum = getattr(metadata, 'max_length', None)
    return (isinstance(minimum, int) and isinstance(maximum, int)
            and minimum <= len(value) <= maximum)


def _compact(id_number: str, metadata: Any) -> str:
    upper = id_number.upper()
    stripped = _SEPARATORS.sub('', upper)
    if any(_slots(mask) < len(mask) for mask in _masks(metadata)):
        return stripped
    trimmed = _WHITESPACE.sub('', upper)
    return trimmed if _fits_length(trimmed, metadata) else stripped


def normalize_id(country: str, id_number: str) -> Optional[str]:
    """Uppercase and remove whitespace, zero-width characters and ``.-/()``.

    With separator-free masks, separators stay if the whitespace-free input has
    an allowed length (preserving Finland's century sign). ``+`` always stays.
    Length and validity are not checked. Country lookup accepts alpha-2/alpha-3
    codes and registered aliases, using only the primary ID type.

    :return: normalized text, or ``None`` for an unsupported country or non-string ID.
    """
    if not isinstance(id_number, str):
        return None
    metadata = _metadata_for(country)
    return None if metadata is None else _compact(id_number, metadata)


def format_id(country: str, id_number: str) -> Optional[str]:
    """Normalize, then insert literals from the first mask with a matching slot count.

    This checks length only, not slot characters or ID validity. For a custom
    country without masks, metadata length bounds select the normalized text.
    It does not change country validators' input handling.

    :return: display text, or ``None`` for unsupported/non-string input or an unmatched length.
    """
    if not isinstance(id_number, str):
        return None
    metadata = _metadata_for(country)
    if metadata is None:
        return None
    value = _compact(id_number, metadata)
    masks = _masks(metadata)
    if not masks:
        return value if _fits_length(value, metadata) else None
    for mask in masks:
        if _slots(mask) == len(value):
            chars = iter(value)
            return ''.join(next(chars) if char in _TOKENS else char for char in mask)
    return None


def get_input_mask(country: str) -> Optional[InputMask]:
    """Return primary-ID masks and an absolute whole-input layout pattern.

    ``#``, ``L`` and ``X`` use ASCII digits/uppercase letters; ``*`` uses Unicode
    non-whitespace. Literals are escaped. A pattern match is not validation;
    length-only formatting can produce text that the pattern rejects. Greek
    identity-card letters remain accepted by the validator and unchanged by
    formatting, but intentionally do not match the ASCII ``L`` pattern.

    :return: frozen mask information, or ``None`` for unsupported countries or missing masks.
    """
    resolved = resolve_country(country)
    if resolved is None:
        return None
    metadata = _metadata_for(resolved)
    masks = _masks(metadata)
    if not masks:
        return None
    alternatives = [''.join(_TOKENS[char] if char in _TOKENS else re.escape(char) for char in mask)
                    for mask in masks]
    pattern = re.compile(r'\A(?:' + '|'.join(alternatives) + r')\Z')
    return InputMask(resolved, masks, pattern)
