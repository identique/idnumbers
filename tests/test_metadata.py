"""
Tests of the typed ``METADATA`` of the ID classes (``idnumbers.nationalid.metadata.IdMetadata``).

Every ID class describes itself with the ten keys that exist since the beginning and with seven descriptive keys:
``country_name``, ``id_type``, ``official_name``, ``display_format``, ``example``, ``checksum_algorithm`` and ``masks``.
The tests check the types of the keys, and that the example and the masks agree with the validator of the class.
"""

import importlib
import pkgutil
import re
from copy import copy
from types import SimpleNamespace
from typing import Any, Iterator, List, Tuple, Type
from unittest import TestCase, main

import idnumbers.nationalid as nationalid_package
from idnumbers import list_supported_countries
from idnumbers.nationalid.metadata import IdMetadata
from idnumbers.registry import CountryEntry

OLD_KEYS = ('iso3166_alpha2', 'min_length', 'max_length', 'parsable', 'checksum', 'regexp', 'alias_of', 'names',
            'links', 'deprecated')
NEW_KEYS = ('country_name', 'id_type', 'official_name', 'display_format', 'example', 'checksum_algorithm', 'masks')

SLOT_CHARS = '#LX*'
SEPARATORS = ' -./()'
STRIPPED = '.-/()'


def slots(mask: str) -> int:
    """The number of characters a mask takes: every character that is not a separator."""
    return sum(1 for char in mask if char in SLOT_CHARS)


def has_separator(mask: str) -> bool:
    return any(char in SEPARATORS for char in mask)


def compact(id_number: str, masks: Tuple[str, ...]) -> str:
    """
    Remove the separators from an example: white space always, and ``.-/()`` when one of the masks has a separator.
    An ID without separators in its masks, such as the Finnish one with its century sign, keeps them.
    """
    result = re.sub(r'\s+', '', id_number)
    if any(has_separator(mask) for mask in masks):
        result = ''.join(char for char in result if char not in STRIPPED)
    return result


def slot_accepts(slot: str, char: str) -> bool:
    if slot == '#':
        return char in '0123456789'
    if slot == 'L':
        return char.isalpha()
    if slot == 'X':
        return char.isalnum()
    return not char.isspace()


def fits(compact_id: str, mask: str) -> bool:
    """Whether a compact ID has as many characters as the mask has slots, and each character suits its slot."""
    slot_chars = [char for char in mask if char in SLOT_CHARS]
    return len(slot_chars) == len(compact_id) and all(slot_accepts(s, c) for s, c in zip(slot_chars, compact_id))


def layout(compact_id: str, mask: str) -> str:
    """Lay the characters of a compact ID into the slots of a mask."""
    assert slots(mask) == len(compact_id)
    chars = iter(compact_id)
    return ''.join(next(chars) if char in SLOT_CHARS else char for char in mask)


def id_classes() -> Iterator[Tuple[CountryEntry, Type[Any]]]:
    for entry in list_supported_countries():
        for cls in entry.id_types:
            yield entry, cls


def all_aliases() -> List[Type[Any]]:
    """Every class created by ``alias_of`` that the country modules and their submodules hold."""
    found: List[Type[Any]] = []
    for info in pkgutil.walk_packages(nationalid_package.__path__, nationalid_package.__name__ + '.'):
        module = importlib.import_module(info.name)
        for obj in vars(module).values():
            metadata = getattr(obj, 'METADATA', None)
            if isinstance(obj, type) and metadata is not None and metadata.alias_of is not None and obj not in found:
                found.append(obj)
    return found


class TestMetadataType(TestCase):
    def test_the_id_classes_are_found(self) -> None:
        self.assertEqual(len(list(id_classes())), 104)

    def test_every_metadata_is_an_id_metadata(self) -> None:
        for entry, cls in id_classes():
            with self.subTest(alpha3=entry.alpha3, cls=cls.__qualname__):
                self.assertIsInstance(cls.METADATA, IdMetadata)
                self.assertIsInstance(cls.METADATA, SimpleNamespace)

    def test_the_old_keys_have_their_types(self) -> None:
        for entry, cls in id_classes():
            with self.subTest(alpha3=entry.alpha3, cls=cls.__qualname__):
                metadata = cls.METADATA
                for key in OLD_KEYS:
                    self.assertIn(key, vars(metadata))
                self.assertIsInstance(metadata.iso3166_alpha2, str)
                self.assertEqual(metadata.iso3166_alpha2, entry.alpha2)
                self.assertIs(type(metadata.min_length), int)
                self.assertIs(type(metadata.max_length), int)
                self.assertLessEqual(metadata.min_length, metadata.max_length)
                self.assertIs(type(metadata.parsable), bool)
                self.assertIs(type(metadata.checksum), bool)
                self.assertIsInstance(metadata.regexp, re.Pattern)
                self.assertIsNone(metadata.alias_of)
                self.assertTrue(metadata.names and all(isinstance(name, str) and name for name in metadata.names))
                self.assertTrue(metadata.links and all(isinstance(link, str) and link for link in metadata.links))
                self.assertIs(type(metadata.deprecated), bool)

    def test_a_copy_is_an_id_metadata(self) -> None:
        for entry, cls in id_classes():
            with self.subTest(alpha3=entry.alpha3, cls=cls.__qualname__):
                duplicate = copy(cls.METADATA)
                self.assertIsInstance(duplicate, IdMetadata)
                self.assertEqual(vars(duplicate), vars(cls.METADATA))

    def test_the_namespace_access_keeps_working(self) -> None:
        metadata = IdMetadata(**{'iso3166_alpha2': 'QQ', 'checksum': True})
        self.assertEqual(metadata.iso3166_alpha2, 'QQ')
        self.assertEqual(vars(metadata), {'iso3166_alpha2': 'QQ', 'checksum': True})
        self.assertTrue(getattr(metadata, 'checksum', False))
        self.assertEqual(getattr(metadata, 'masks', ()), ())
        self.assertEqual(metadata, SimpleNamespace(iso3166_alpha2='QQ', checksum=True))


class TestNewKeys(TestCase):
    def test_every_class_has_all_the_new_keys(self) -> None:
        for entry, cls in id_classes():
            with self.subTest(alpha3=entry.alpha3, cls=cls.__qualname__):
                for key in NEW_KEYS:
                    self.assertIn(key, vars(cls.METADATA))

    def test_the_new_keys_are_valid(self) -> None:
        for entry, cls in id_classes():
            with self.subTest(alpha3=entry.alpha3, cls=cls.__qualname__):
                self.check_class(entry, cls)

    def check_class(self, entry: CountryEntry, cls: Type[Any]) -> None:
        metadata = cls.METADATA
        for key in ('country_name', 'id_type', 'display_format', 'example'):
            self.assertIs(type(getattr(metadata, key)), str, key)
            self.assertTrue(getattr(metadata, key).strip(), key)
        for key in ('official_name', 'checksum_algorithm'):
            value = getattr(metadata, key)
            self.assertTrue(value is None or (type(value) is str and value.strip()), key)
        self.assertEqual(metadata.country_name, entry.name)
        self.assertEqual(metadata.checksum_algorithm is None, not metadata.checksum)
        self.assertNotEqual(metadata.official_name, metadata.id_type)
        self.check_masks(cls)
        self.check_example(cls)

    def check_masks(self, cls: Type[Any]) -> None:
        masks = cls.METADATA.masks
        self.assertIs(type(masks), tuple)
        self.assertTrue(masks)
        self.assertEqual(len(masks), len(set(masks)))
        for mask in masks:
            self.assertIs(type(mask), str)
            self.assertTrue(mask)
            self.assertTrue(all(char in SLOT_CHARS + SEPARATORS for char in mask), mask)
            self.assertTrue(slots(mask), mask)
            self.assertTrue(cls.METADATA.min_length <= slots(mask) <= cls.METADATA.max_length, mask)

    def check_example(self, cls: Type[Any]) -> None:
        metadata = cls.METADATA
        example = metadata.example
        self.assertIs(cls.validate(example), True, example)
        if metadata.parsable:
            self.assertIsNotNone(cls.parse(example), example)
        # The example is written in the first (preferred) layout of the masks, as docs/nationalid/METADATA.md states.
        first = metadata.masks[0]
        self.assertEqual(len(example), len(first), f'{example} is not written in {first}')
        for char, mask_char in zip(example, first):
            if mask_char in SLOT_CHARS:
                self.assertTrue(slot_accepts(mask_char, char), f'{example} is not written in {first}')
            else:
                self.assertEqual(char, mask_char, f'{example} is not written in {first}')
        compact_id = compact(example, metadata.masks)
        self.assertLessEqual(metadata.min_length, len(compact_id), example)
        self.assertLessEqual(len(compact_id), metadata.max_length, example)
        # A mask of the same length can describe another layout of the same length (NZL NHI: LLL#### and LLL##LL),
        # so only the masks whose slot types fit the example are laid out; at least one must.
        fitting = [mask for mask in metadata.masks if fits(compact_id, mask)]
        self.assertTrue(fitting, f'no mask for {example}')
        for mask in fitting:
            laid = layout(compact_id, mask)
            with self.subTest(mask=mask):
                self.assertIs(cls.validate(laid), True, f'{mask} -> {laid}')


class TestAliases(TestCase):
    def test_a_country_module_alias_reads_as_its_target(self) -> None:
        for entry in list_supported_countries():
            with self.subTest(alpha3=entry.alpha3):
                national_id = entry.national_id
                target = national_id.METADATA.alias_of
                if target is None:
                    self.assertIn(national_id, entry.id_types)
                    continue
                self.check_alias(national_id, target)

    def test_every_alias_reads_as_its_target(self) -> None:
        aliases = all_aliases()
        self.assertGreaterEqual(len(aliases), 70)
        for alias in aliases:
            with self.subTest(alias=f'{alias.__module__}.{alias.__qualname__}'):
                self.check_alias(alias, alias.METADATA.alias_of)

    def check_alias(self, alias: Type[Any], target: Type[Any]) -> None:
        self.assertIsNot(alias, target)
        self.assertTrue(issubclass(alias, target))
        self.assertIs(alias.METADATA.alias_of, target)
        self.assertEqual(alias.__name__, target.__name__)
        self.assertEqual(alias.__qualname__, target.__qualname__)
        self.assertEqual(alias.__module__, target.__module__)
        self.assertEqual(alias.__doc__, target.__doc__)
        self.assertIsInstance(alias.METADATA, IdMetadata)
        alias_vars = {key: value for key, value in vars(alias.METADATA).items() if key != 'alias_of'}
        target_vars = {key: value for key, value in vars(target.METADATA).items() if key != 'alias_of'}
        self.assertEqual(alias_vars, target_vars)

    def test_the_alias_of_the_australian_primary_is_the_driver_licence(self) -> None:
        from idnumbers.nationalid import AUS
        self.assertEqual(AUS.NationalID.__name__, 'DriverLicenseNumber')
        self.assertIsNot(AUS.NationalID, AUS.DriverLicenseNumber)
        self.assertNotIn('AliasType', repr(AUS.NationalID))


if __name__ == '__main__':
    main()
