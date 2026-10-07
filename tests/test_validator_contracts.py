"""Deterministic contract checks for every registered ID type.

Hypothesis runs 100 arbitrary Unicode strings per class, without an example database.
A failing unittest names the country/type and Hypothesis prints its minimized input.
Mutation checks exhaust the synthetic example's digits, not all possible valid IDs.
Valid-example, mask and in-range length checks remain in test_metadata.py.
This module checks regexp agreement using that suite's existing compact-layout helper.
"""
from typing import Any, Callable, Type
from unittest import TestCase

from tests.helpers.hypothesis_setup import given, settings, strategies as st

from tests.helpers.checksum_limits import SINGLE_DIGIT_CHANGE_UNDETECTED
from tests.helpers.contract import (
    CHECK_CHARACTER_INDEX, check_character_mutations, iter_id_classes, length_out_of_range_variants,
    single_digit_mutations,
)
from tests.test_metadata import class_key, compact



class TestValidatorContracts(TestCase):
    def test_examples_agree_with_metadata_regexp(self) -> None:
        for entry, cls in iter_id_classes():
            metadata = cls.METADATA
            candidates = (metadata.example, compact(metadata.example, metadata.masks))
            with self.subTest(country=entry.alpha3, cls=class_key(cls)):
                self.assertTrue(any(metadata.regexp.fullmatch(value) for value in candidates))

    def test_metadata_methods_are_consistent(self) -> None:
        for entry, cls in iter_id_classes():
            with self.subTest(country=entry.alpha3, cls=class_key(cls)):
                self.assertEqual(cls.METADATA.parsable, callable(getattr(cls, 'parse', None)))
                self.assertEqual(cls.METADATA.checksum, callable(getattr(cls, 'checksum', None)))

    def test_out_of_range_lengths_are_rejected(self) -> None:
        for entry, cls in iter_id_classes():
            for value in length_out_of_range_variants(cls):
                with self.subTest(country=entry.alpha3, cls=class_key(cls), value=value):
                    self.assertIs(cls.validate(value), False)

    def test_changed_check_characters_are_rejected(self) -> None:
        for entry, cls in iter_id_classes():
            if cls.METADATA.checksum:
                for value in check_character_mutations(
                        cls.METADATA.example, CHECK_CHARACTER_INDEX.get(class_key(cls), -1)):
                    with self.subTest(country=entry.alpha3, cls=class_key(cls), value=value):
                        self.assertIs(cls.validate(value), False)

    def test_single_digit_mutations_and_exception_staleness(self) -> None:
        checksum_keys = set()
        for entry, cls in iter_id_classes():
            if not cls.METADATA.checksum:
                continue
            key = class_key(cls)
            checksum_keys.add(key)
            with self.subTest(country=entry.alpha3, cls=key):
                accepted = tuple(value for value in single_digit_mutations(cls.METADATA.example)
                                 if cls.validate(value))
                self.assertEqual(accepted, SINGLE_DIGIT_CHANGE_UNDETECTED.get(key, ()))
        self.assertLessEqual(set(SINGLE_DIGIT_CHANGE_UNDETECTED), checksum_keys)
        self.assertLessEqual(set(CHECK_CHARACTER_INDEX), checksum_keys)


def unicode_contract(cls: Type[Any]) -> Callable[..., None]:
    @settings(database=None, derandomize=True, max_examples=100)
    @given(st.text())
    def test(self: TestCase, value: str) -> None:
        self.assertIs(type(cls.validate(value)), bool)
    return test


# Separate properties guarantee the full sample budget for EVERY secondary type too.
for _entry, _cls in iter_id_classes():
    setattr(TestValidatorContracts, f'test_unicode_{_entry.alpha3}_{_cls.__name__}', unicode_contract(_cls))
