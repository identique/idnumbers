"""Registry-wide contract helpers; runtime code never imports this module.

The metadata suite owns valid-example, mask and in-range length checks.
Reuse its compact-layout helper instead of inventing another normalization rule.
"""
from typing import Any, Iterator, Tuple, Type

from idnumbers import list_supported_countries
from idnumbers.registry import CountryEntry
from tests.test_metadata import compact


def iter_id_classes() -> Iterator[Tuple[CountryEntry, Type[Any]]]:
    """Yield every registered ID type, including secondary types (not alias classes)."""
    for entry in list_supported_countries():
        for cls in entry.id_types:
            yield entry, cls


def single_digit_mutations(value: str) -> Iterator[str]:
    """Change exactly one ASCII digit, leaving layout and other characters intact."""
    for index, char in enumerate(value):
        if char in '0123456789':
            for digit in '0123456789':
                if digit != char:
                    yield value[:index] + digit + value[index + 1:]


def check_character_mutations(value: str, index: int = -1) -> Iterator[str]:
    """Index is among ASCII alphanumerics, so separators do not change its meaning."""
    positions = [i for i, char in enumerate(value) if char.isascii() and char.isalnum()]
    position = positions[index]
    for char in '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ':
        if char != value[position]:
            yield value[:position] + char + value[position + 1:]


def length_out_of_range_variants(cls: Type[Any]) -> Tuple[str, ...]:
    """Lengths outside metadata bounds both as written and in compact layout."""
    metadata = cls.METADATA
    value = compact(metadata.example, metadata.masks)
    padding = '1' * max(1, metadata.max_length + 1 - len(value))
    return (value[:max(0, metadata.min_length - 1)], value + padding, metadata.example + padding)
