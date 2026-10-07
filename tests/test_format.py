"""Primary mask roundtrips and normalization without invoking validation."""
import dataclasses
import os
import re
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import patch

from idnumbers import InputMask, format_id, get_input_mask, normalize_id, register
from idnumbers import list_supported_countries
from idnumbers.nationalid import GRC, SWE
from tests.test_api import isolated_registry
from tests.test_metadata import MASK_SAMPLES, class_key, compact, fits, layout


class TestPrimaryFormats(TestCase):
    def test_all_primary_examples_and_accepted_mask_variants(self):
        entries = list_supported_countries()
        self.assertEqual(len(entries), 78)
        for entry in entries:
            cls = entry.national_id
            metadata = cls.METADATA
            samples = [metadata.example, *MASK_SAMPLES.get(class_key(cls), ())]
            value = compact(metadata.example, metadata.masks)
            samples += [layout(value, mask) for mask in metadata.masks if fits(value, mask)]
            for sample in samples:
                with self.subTest(country=entry.alpha3, sample=sample):
                    self.assertTrue(cls.validate(sample))
                    formatted = format_id(entry.alpha3, sample)
                    self.assertIsNotNone(formatted)
                    self.assertTrue(cls.validate(formatted))
                    self.assertEqual(normalize_id(entry.alpha3, formatted), normalize_id(entry.alpha3, sample))
                    mask = get_input_mask(entry.alpha2.lower())
                    self.assertIsInstance(mask, InputMask)
                    self.assertEqual(mask.country_code, entry.alpha3)
                    self.assertEqual(mask.masks, metadata.masks)
                    self.assertIsNotNone(mask.pattern.fullmatch(formatted))
                    self.assertEqual(format_id(entry.alpha2.lower(), sample), formatted)

    def test_ascii_pattern_intentionally_excludes_greek_letters(self):
        sample = 'ΑΒ-123456'
        self.assertTrue(GRC.IdentityCard.validate(sample))
        self.assertEqual(format_id('GR', sample), sample)
        self.assertEqual(normalize_id('GR', sample), 'ΑΒ123456')
        self.assertIsNone(get_input_mask('GR').pattern.fullmatch(sample))
        self.assertIsNotNone(get_input_mask('GR').pattern.fullmatch('AB-123456'))

    def test_primary_selection(self):
        self.assertEqual(get_input_mask('AU').masks, get_input_mask('AUS').masks)
        self.assertEqual(get_input_mask('GRC').masks, GRC.IdentityCard.METADATA.masks)
        self.assertEqual(get_input_mask('AU').masks[0], '### ### ###')

    def test_compact_acceptance_of_builtin_examples(self):
        rejected = []
        for entry in list_supported_countries():
            value = normalize_id(entry.alpha3, entry.national_id.METADATA.example)
            if not entry.national_id.validate(value):
                rejected.append(entry.alpha3)
        self.assertEqual(rejected, ['CHE', 'CHL', 'KOR', 'USA'])


class TestNormalization(TestCase):
    def test_separators_lowercase_and_zero_width(self):
        self.assertEqual(normalize_id('BR', ' (111).444/777-35 '), '11144477735')
        self.assertEqual(normalize_id('TW', 'a123456789'), 'A123456789')
        for char in '\t\n\r \u00a0\u2003\u200b\u200c\u200d\u2060\ufeff':
            with self.subTest(char=repr(char)):
                self.assertEqual(normalize_id('TW', char + 'a123' + char + '456789' + char), 'A123456789')
        self.assertEqual(format_id('BR', ' (111).444/777-35 '), '111.444.777-35')

    def test_finland_and_sweden_signs(self):
        for sign in '-+A':
            sample = '131052' + sign + '308t'
            self.assertEqual(normalize_id('FI', sample), sample.upper())
            self.assertEqual(format_id('FI', sample), sample.upper())
        self.assertEqual(normalize_id('FI', '131052-308'), '131052308')
        self.assertEqual(normalize_id('FI', '13.1052-308T'), '131052308T')
        for sample in ['820908-8882', '19820908-8882']:
            self.assertEqual(normalize_id('SE', sample), sample.replace('-', ''))
            self.assertEqual(format_id('SE', sample), sample)
        self.assertEqual(normalize_id('SE', '820908+8882'), '820908+8882')
        self.assertEqual(format_id('SE', '820908+8882'), '820908+8882')
        self.assertEqual(normalize_id('BR', '111+44477735'), '111+44477735')

    def test_sweden_valid_century_sign_roundtrip(self):
        for sample in ['811218+9876', '19811218+9876']:
            self.assertTrue(SWE.NationalID.validate(sample))
            for country in ['se', 'SE', 'swe', 'SWE']:
                for text in [sample, ' \t' + sample[:3] + '\u200b' + sample[3:] + '\n']:
                    with self.subTest(country=country, text=text):
                        self.assertEqual(normalize_id(country, text), sample)
                        formatted = format_id(country, text)
                        self.assertEqual(formatted, sample)
                        self.assertTrue(SWE.NationalID.validate(formatted))
                        self.assertEqual(normalize_id(country, formatted), normalize_id(country, text))
                        self.assertEqual(format_id(country, formatted), formatted)
            mask = get_input_mask('se')
            self.assertEqual(mask.masks, ('######-####', '########-####'))
            self.assertIsNone(mask.pattern.fullmatch(sample))
            self.assertIsNotNone(mask.pattern.fullmatch(sample.replace('+', '-')))
        with patch.object(SWE.NationalID, 'validate', side_effect=AssertionError('must not validate')):
            self.assertEqual(format_id('se', '811218+9876'), '811218+9876')
            self.assertEqual(format_id('SWE', '19811218+9876'), '19811218+9876')
            self.assertEqual(format_id('SE', 'AAAAAA+BBBB'), 'AAAAAA+BBBB')

    def test_sweden_malformed_century_signs_are_not_relocated(self):
        for sample in ['+8112189876', '81121+89876', '8112189876+',
                       '+198112189876', '1981121+89876', '198112189876+',
                       '811218++9876', '19811218++9876', '811+218+9876']:
            with self.subTest(sample=sample):
                self.assertFalse(SWE.NationalID.validate(sample))
                self.assertEqual(normalize_id('SE', sample), sample)
                formatted = format_id('SE', sample)
                self.assertFalse(SWE.NationalID.validate(formatted))
        # Length-only formatting still leaves a misplaced sign in its slot.
        self.assertEqual(format_id('SE', '81121+9876'), '81121+-9876')

    def test_no_length_or_validity_check(self):
        self.assertEqual(normalize_id('TW', ''), '')
        self.assertEqual(normalize_id('BR', 'a--b'), 'AB')
        self.assertEqual(normalize_id('BR', 'abc' * 100), 'ABC' * 100)
        self.assertIsNone(format_id('TW', ''))
        self.assertIsNone(format_id('BR', '123'))
        self.assertEqual(format_id('BR', 'a' * 11), 'AAA.AAA.AAA-AA')
        self.assertIsNone(get_input_mask('BR').pattern.fullmatch('AAA.AAA.AAA-AA'))

    def test_bad_arguments(self):
        for country in ['XX', '', ' TW', 'TWN ', 'ın', None, 12, [], {}]:
            self.assertIsNone(normalize_id(country, '123'))
            self.assertIsNone(format_id(country, '123'))
            self.assertIsNone(get_input_mask(country))
        for value in [None, 12, True, [], {}, b'123']:
            self.assertIsNone(normalize_id('TW', value))
            self.assertIsNone(format_id('TW', value))

    def test_lazy_imports(self):
        code = """
import sys
import idnumbers
assert not any(n.startswith('idnumbers.nationalid') for n in sys.modules)
assert idnumbers.normalize_id('XX', '1') is None
assert idnumbers.format_id('XX', '1') is None
assert idnumbers.get_input_mask('XX') is None
assert idnumbers.format_id('TW', None) is None
assert not any(n.startswith('idnumbers.nationalid') for n in sys.modules)
"""
        root = str(Path(__file__).resolve().parents[1])
        result = subprocess.run([sys.executable, '-c', code], cwd=root,
                                env={**os.environ, 'PYTHONPATH': root}, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)


class TestCustomMasks(TestCase):
    def custom(self, **metadata):
        class Custom:
            METADATA = SimpleNamespace(iso3166_alpha2='QQ', **metadata)

            @staticmethod
            def validate(value):
                raise AssertionError('formatting must never validate')
        register('QQQ', Custom, aliases=['custom-format'])

    def test_alias_first_matching_mask_and_frozen_fields(self):
        with isolated_registry():
            self.custom(masks=('##-LX*', '##/LX*', '###'))
            self.assertEqual(normalize_id('custom-format', '12/a3!'), '12A3!')
            self.assertEqual(format_id('qq', '12/a3!'), '12-A3!')
            self.assertEqual(format_id('QQQ', '123'), '123')
            self.assertIsNone(format_id('QQQ', '1'))
            mask = get_input_mask('custom-format')
            self.assertEqual(mask.country_code, 'QQQ')
            self.assertIs(type(mask.masks), tuple)
            self.assertIsInstance(mask.pattern, re.Pattern)
            self.assertEqual([f.name for f in dataclasses.fields(mask)], ['country_code', 'masks', 'pattern'])
            with self.assertRaises(dataclasses.FrozenInstanceError):
                mask.country_code = 'BAD'
            for text in ['12-A3!', '12/A3é', '123']:
                self.assertIsNotNone(mask.pattern.fullmatch(text))
            for text in ['１２-A3!', '12-a3!', '12-A３!', '12-A3 ', '12-A3!\n', 'x123']:
                self.assertIsNone(mask.pattern.match(text))

    def test_sweden_sign_handling_does_not_apply_to_other_countries(self):
        with isolated_registry():
            self.custom(masks=('######-####', '########-####'))
            self.assertIsNone(format_id('custom-format', '811218+9876'))
            self.assertIsNone(format_id('QQ', '19811218+9876'))
            self.assertEqual(format_id('QQQ', '8112189876'), '811218-9876')

    def test_escaped_literal(self):
        with isolated_registry():
            self.custom(masks=('(##)./#+',))
            self.assertEqual(format_id('QQ', '123'), '(12)./3+')
            pattern = get_input_mask('QQ').pattern
            self.assertIsNotNone(pattern.fullmatch('(12)./3+'))
            self.assertIsNone(pattern.fullmatch('x12xy3+'))

    def test_no_masks_fallback(self):
        for masks in [None, (), []]:
            with self.subTest(masks=masks), isolated_registry():
                self.custom(min_length=3, max_length=4, **({} if masks is None else {'masks': masks}))
                self.assertIsNone(get_input_mask('QQ'))
                self.assertEqual(normalize_id('QQ', 'a-b'), 'A-B')
                self.assertEqual(format_id('QQ', 'a-b'), 'A-B')
                self.assertEqual(normalize_id('QQ', 'a--bc'), 'ABC')
                self.assertEqual(format_id('QQ', 'a--bc'), 'ABC')
                self.assertIsNone(format_id('QQ', 'x'))

    def test_minimal_registry_metadata(self):
        with isolated_registry():
            self.custom()
            self.assertEqual(normalize_id('QQ', 'a-b'), 'AB')
            self.assertIsNone(format_id('QQ', 'a-b'))
            self.assertIsNone(get_input_mask('QQ'))
