"""Best-effort diagnostics: frozen witnesses and adversarial custom validators."""

import asyncio
import re
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from threading import Barrier
from types import SimpleNamespace
from unittest import TestCase

import idnumbers
from idnumbers import FailureReason as R, api, failure_reason, parse_id_info, validate
from idnumbers.nationalid import AUS, BEL, BGR, CHL, ITA, LKA, TWN
from idnumbers.nationalid import util
from tests.helpers.failure_reasons import iter_reason_matrix
from tests.helpers.inventory import registered_id_classes
from tests.helpers.contract import CHECK_CHARACTER_INDEX, check_character_mutations, iter_id_classes
from tests.test_api import isolated_registry


def rejecting(pattern=r"(?P<checksum>\d)", checksum=None, validator=None):
    class Custom:
        METADATA = SimpleNamespace(regexp=re.compile(pattern), min_length=1, max_length=1)

        @staticmethod
        def validate(value):
            return False if validator is None else validator(value)

    if checksum is not None:
        Custom.checksum = staticmethod(checksum)
    return Custom


class TestReasonMatrix(TestCase):
    def test_all_classes(self):
        rows = list(iter_reason_matrix())
        self.assertSetEqual({row.key for row in rows}, registered_id_classes())
        self.assertEqual(len(rows), len(registered_id_classes()))
        for row in rows:
            self.assertTrue(row.checksum_note)
            self.assertTrue(row.birthdate_note)
            self.assertEqual(row.valid.id_number, row.id_class.METADATA.example)
            for vector in (row.valid, *row.length, row.format, row.checksum, row.birthdate):
                if vector is None:
                    continue
                with self.subTest(cls=row.key, value=vector.id_number, expected=vector.expected):
                    self.assertEqual(row.id_class.validate(vector.id_number), vector.expected is None)
                    self.assertEqual(failure_reason(row.id_class, vector.id_number), vector.expected)
                    # Primary aliases and both unified paths must agree with the per-class result.
                    primary = idnumbers.get_validator(row.country)
                    if primary.METADATA.alias_of is row.id_class:
                        self.assertEqual(failure_reason(primary, vector.id_number), vector.expected)
                        result = validate(row.country, vector.id_number)
                        parsed = parse_id_info(row.country, vector.id_number)
                        self.assertEqual(result.reason, vector.expected)
                        if vector.expected is not None:
                            self.assertEqual(parsed.reason, vector.expected)

    def test_checksum_witnesses_change_only_check_character(self):
        counts = {R.CHECKSUM_MISMATCH: 0, R.VALIDATION_FAILED: 0}
        witnesses = 0
        rows = list(iter_reason_matrix())
        for row in rows:
            if row.checksum is None:
                continue
            with self.subTest(cls=row.key):
                self.assertIn(
                    row.checksum.id_number,
                    check_character_mutations(row.valid.id_number, CHECK_CHARACTER_INDEX.get(row.key, -1)),
                )
                self.assertIsNotNone(util.match_regexp(row.checksum.id_number, row.id_class.METADATA.regexp))
                self.assertFalse(row.id_class.validate(row.checksum.id_number))
                counts[row.checksum.expected] += 1
                witnesses += 1
        self.assertGreater(witnesses, 0)
        self.assertEqual(counts, {R.CHECKSUM_MISMATCH: witnesses, R.VALIDATION_FAILED: 0})
        # A dropped checksum witness fails here by class name, even when the guides are regenerated in the same change.
        self.assertSetEqual(
            {row.key for row in rows if row.checksum is not None},
            {row.key for row in rows if row.id_class.METADATA.checksum},
        )

    def test_all_date_migrations_have_witnesses(self):
        rows = list(iter_reason_matrix())
        expected_countries = {
            "ALB",
            "BEL",
            "BGR",
            "BIH",
            "CHN",
            "CZE",
            "DNK",
            "EGY",
            "EST",
            "FIN",
            "HUN",
            "IDN",
            "ISL",
            "ITA",
            "KAZ",
            "KOR",
            "KWT",
            "LTU",
            "LUX",
            "LVA",
            "MEX",
            "MKD",
            "MNE",
            "MYS",
            "NOR",
            "POL",
            "ROU",
            "SRB",
            "SVK",
            "SVN",
            "SWE",
            "ZAF",
        }
        dated = [row for row in rows if row.birthdate is not None]
        self.assertEqual({row.country for row in dated}, expected_countries)
        self.assertEqual(len(dated), 35)
        self.assertTrue(all(row.birthdate.expected == R.INVALID_BIRTHDATE for row in dated))

    def test_legacy_date_policies(self):
        # Belgium's unknown month/day is valid and must not record a date error.
        for value in ("85000003306", "85010003313"):
            self.assertIsNone(failure_reason(BEL.NationalID, value))
        # ITA chooses 2000 first, falling back to 1900 only for future dates.
        self.assertEqual(ITA.FiscalCode.extract_birthday("00", "B", "29")[0], date(2000, 2, 29))
        self.assertIsNone(ITA.FiscalCode.extract_birthday("99", "B", "29"))
        # LKA's legacy day 366 rolls into the next year for non-leap years.
        self.assertEqual(util.birth_date(1990, 1, 1), date(1990, 1, 1))
        bad_year = "000001200001"
        # The old ordinal rules are deliberately not changed; year zero is a calendar failure.
        for digit in "0123456789":
            value = bad_year[:-1] + digit
            if LKA.NationalID.checksum(value):
                self.assertEqual(failure_reason(LKA.NationalID, value), R.INVALID_BIRTHDATE)
                break
        else:
            self.fail("No repaired LKA checksum")

    def test_ordinal_rollover_is_not_calendar_failure(self):
        base = "199036600001"
        witnesses = [base[:-1] + digit for digit in "0123456789" if LKA.NationalID.validate(base[:-1] + digit)]
        self.assertTrue(witnesses)
        for value in witnesses:
            self.assertEqual(LKA.NationalID.parse(value)["yyyymmdd"], date(1991, 1, 1))
            self.assertIsNone(failure_reason(LKA.NationalID, value))


class TestDerivation(TestCase):
    def test_exports(self):
        self.assertIs(idnumbers.failure_reason, api.failure_reason)
        self.assertIn("failure_reason", api.__all__)
        self.assertIsNone(failure_reason(AUS.MedicareNumber, "2123 45670 1"))

    def test_length_format_precedence(self):
        cls = rejecting(checksum=lambda value: False)
        for value, expected in [
            ("", R.INVALID_LENGTH),
            ("11", R.INVALID_LENGTH),
            ("x", R.INVALID_FORMAT),
            ("１", R.INVALID_FORMAT),
            ("1\n", R.CHECKSUM_MISMATCH),
        ]:
            self.assertEqual(failure_reason(cls, value), expected)
        for value in (None, 1, b"1", [], object()):
            self.assertEqual(failure_reason(cls, value), R.INVALID_FORMAT)

    def test_separator_candidates_do_not_change_validity(self):
        self.assertEqual(failure_reason(TWN.NationalID, "A12345"), R.INVALID_LENGTH)
        self.assertEqual(failure_reason(TWN.NationalID, "A123456788"), R.CHECKSUM_MISMATCH)
        self.assertEqual(validate("ZA", "7602300675085").reason, R.INVALID_BIRTHDATE)
        cls = rejecting(checksum=lambda value: False)
        self.assertEqual(failure_reason(cls, " (1) .-/\t"), R.CHECKSUM_MISMATCH)
        self.assertFalse(cls.validate(" (1) .-/\t"))
        # Original and stripped candidates both match: one inconclusive candidate prevents a checksum reason.
        cls = rejecting(r"\d[ .-]?", checksum=lambda value: False if len(value) == 2 else None)
        self.assertEqual(failure_reason(cls, "1 "), R.VALIDATION_FAILED)
        self.assertEqual(failure_reason(rejecting(r"\d ?", checksum=lambda value: False), "1 "), R.CHECKSUM_MISMATCH)
        self.assertEqual(failure_reason(TWN.NationalID, " " + TWN.NationalID.METADATA.example), R.VALIDATION_FAILED)

    def test_checksum_return_contract(self):
        for computed, expected in [
            (False, R.CHECKSUM_MISMATCH),
            (True, R.VALIDATION_FAILED),
            (None, R.VALIDATION_FAILED),
            (0, R.CHECKSUM_MISMATCH),
            (1, R.VALIDATION_FAILED),
            ("X", R.CHECKSUM_MISMATCH),
        ]:
            with self.subTest(computed=computed):
                self.assertEqual(failure_reason(rejecting(checksum=lambda value: computed), "1"), expected)
        self.assertEqual(failure_reason(rejecting(checksum=lambda value: 0), "0"), R.VALIDATION_FAILED)
        self.assertEqual(failure_reason(rejecting(r"\d", checksum=lambda value: 0), "1"), R.VALIDATION_FAILED)
        self.assertEqual(
            failure_reason(rejecting(r"(?P<checksum>2)?1", checksum=lambda value: 0), "1"), R.VALIDATION_FAILED
        )

    def test_metadata_and_checksum_errors(self):
        def boom(value):
            raise RuntimeError("boom")

        for metadata in (
            None,
            SimpleNamespace(),
            SimpleNamespace(regexp="not compiled"),
            SimpleNamespace(regexp=re.compile("x"), min_length=None, max_length=1),
        ):
            cls = rejecting()
            cls.METADATA = metadata
            self.assertEqual(failure_reason(cls, "1"), R.VALIDATION_FAILED)
        self.assertEqual(failure_reason(rejecting(checksum=boom), "1"), R.VALIDATION_FAILED)
        self.assertEqual(failure_reason(rejecting(validator=boom), "1"), R.VALIDATION_FAILED)
        self.assertEqual(failure_reason(object, "1"), R.VALIDATION_FAILED)
        self.assertIsNone(failure_reason(rejecting(validator=lambda value: True), None))

    def test_birthdate_and_checksum_precedence(self):
        def bad_date(value):
            util.birth_date(2000, 2, 31)
            return False

        for computed, expected in [
            (False, R.CHECKSUM_MISMATCH),
            (None, R.INVALID_BIRTHDATE),
            (True, R.INVALID_BIRTHDATE),
        ]:
            self.assertEqual(
                failure_reason(rejecting(checksum=lambda value: computed, validator=bad_date), "1"), expected
            )
        self.assertEqual(failure_reason(rejecting(validator=bad_date), "x"), R.INVALID_FORMAT)

    def test_trace_exception_cleanup(self):
        count = 0

        def later_boom(value):
            nonlocal count
            count += 1
            if count > 1:
                util.birth_date(2000, 2, 31)
                raise ValueError("traced exception")
            return False

        self.assertEqual(failure_reason(rejecting(validator=later_boom), "1"), R.VALIDATION_FAILED)
        self.assertIsNone(util._birth_date_trace.get())
        self.assertEqual(failure_reason(rejecting(), "1"), R.VALIDATION_FAILED)

    def test_unified_path_does_not_repeat_initial_validation(self):
        calls = []
        cls = rejecting(checksum=lambda value: False, validator=lambda value: calls.append(value) or False)
        self.assertEqual(api._check("QQQ", cls, "1").reason, R.CHECKSUM_MISMATCH)
        self.assertEqual(calls, ["1"])

    def test_custom_registry_lockstep(self):
        cls = rejecting(checksum=lambda value: False)
        cls.METADATA.iso3166_alpha2 = "QQ"
        with isolated_registry():
            idnumbers.register("QQQ", cls, alpha2="QQ")
            self.assertEqual(validate("qq", "1").reason, R.CHECKSUM_MISMATCH)
            self.assertEqual(parse_id_info("QQQ", "1").reason, R.CHECKSUM_MISMATCH)


class TestTraceIsolation(TestCase):
    def test_helper_and_nested_contexts(self):
        self.assertIsNone(util._birth_date_trace.get())
        self.assertIsNone(util.birth_date(1900, 2, 29))
        self.assertIsNone(util._birth_date_trace.get())
        token = util._birth_date_trace.set(False)
        try:
            self.assertEqual(util.birth_date(2000, 2, 29), date(2000, 2, 29))
            self.assertFalse(util._birth_date_trace.get())
            inner = rejecting(validator=lambda value: util.birth_date(2000, 2, 31) is not None)
            self.assertEqual(failure_reason(inner, "1"), R.INVALID_BIRTHDATE)
            self.assertFalse(util._birth_date_trace.get())

            def outer(value):
                if util._birth_date_trace.get() is not None:
                    # Only the private derivation starts a new trace; nested calls restore it.
                    failure_reason(inner, "1")
                    self.assertFalse(util._birth_date_trace.get())
                return False

            self.assertEqual(failure_reason(rejecting(validator=outer), "1"), R.VALIDATION_FAILED)
            self.assertFalse(util._birth_date_trace.get())
            util.birth_date(2000, 2, 31)
            self.assertTrue(util._birth_date_trace.get())
        finally:
            util._birth_date_trace.reset(token)
        self.assertIsNone(util._birth_date_trace.get())

    def test_nested_unified_calls(self):
        inner = rejecting(validator=lambda value: util.birth_date(2000, 2, 31) is not None)
        inner.METADATA.iso3166_alpha2 = "QQ"
        with isolated_registry():
            idnumbers.register("QQQ", inner, alpha2="QQ")
            for diagnose in (validate, parse_id_info):

                def outer(value):
                    traced = util._birth_date_trace.get()
                    self.assertEqual(diagnose("QQQ", "1").reason, R.INVALID_BIRTHDATE)
                    self.assertIs(util._birth_date_trace.get(), traced)
                    return False

                self.assertEqual(failure_reason(rejecting(validator=outer), "1"), R.VALIDATION_FAILED)
        self.assertIsNone(util._birth_date_trace.get())

    def test_threads(self):
        barrier = Barrier(2)

        def worker(invalid):
            token = util._birth_date_trace.set(False)
            try:
                if invalid:
                    util.birth_date(2000, 2, 31)
                barrier.wait(timeout=10)
                return util._birth_date_trace.get()
            finally:
                util._birth_date_trace.reset(token)

        with ThreadPoolExecutor(max_workers=2) as pool:
            self.assertEqual(list(pool.map(worker, [True, False])), [True, False])
        self.assertIsNone(util._birth_date_trace.get())

    def test_async_tasks(self):
        async def worker(invalid):
            token = util._birth_date_trace.set(False)
            try:
                if invalid:
                    util.birth_date(2000, 2, 31)
                await asyncio.sleep(0)
                return util._birth_date_trace.get()
            finally:
                util._birth_date_trace.reset(token)

        async def run():
            return await asyncio.gather(worker(True), worker(False))

        self.assertEqual(asyncio.run(run()), [True, False])
        self.assertIsNone(util._birth_date_trace.get())


_PACKAGE = "idnumbers.nationalid."
# The 14 classes whose regexp gained a named `checksum` group in #506 (module.ClassName under idnumbers.nationalid).
COMPUTED_CHECKSUM_GROUP_KEYS = tuple(
    _PACKAGE + key
    for key in (
        "aus.medicare.MedicareNumber",
        "aus.tax_file.TaxFileNumber",
        "bgr.unifed_id_code.UnifiedIdCode",
        "chl.national_id.NationalID",
        "col.unique_persional_id.UniquePersonalID",
        "grc.tax_id.TaxIdentityNumber",
        "hkg.national_id.NationalID",
        "irn.national_id.NationalID",
        "isr.national_id.NationalID",
        "jpn.national_id.MyNumber",
        "lva.personal_code.PersonalCode",
        "tur.national_id.NationalID",
        "ukr.entity_id.EntityIDNumber",
        "ukr.taxpayer_id.TaxpayerIDNumber",
    )
)

# The regexps before #506, verbatim. The refactor into one `checksum` group must not change what matches.
OLD_PATTERNS = {
    _PACKAGE + key: pattern
    for key, pattern in {
        "aus.medicare.MedicareNumber": (
            r"^("
            r"[2-6]\d{10}|[2-6]\d{3} \d{5} \d|[2-6]\d{3}-\d{5}-\d|"
            r"[2-6]\d{9}|[2-6]\d{9}([-/]\d)?|"
            r"[2-6]\d{3} \d{5} \d([-/]\d)?|[2-6]\d{3}-\d{5}-\d([-/]\d)?|"
            r"[2-6]\d{3} \d{5} \d \d|[2-6]\d{3}-\d{5}-\d-\d"
            r")$"
        ),
        "aus.tax_file.TaxFileNumber": r"^(\d{9}|\d{8})$",
        "bgr.unifed_id_code.UnifiedIdCode": r"^(\d{9}|\d{13})$",
        "chl.national_id.NationalID": r"^(\d{1,2}\.\d{3}\.\d{3}-[\dKk])$",
        "col.unique_persional_id.UniquePersonalID": r"^(\d{2,3}\.?\d{3}\.?\d{3}-?\d)$",
        "grc.tax_id.TaxIdentityNumber": r"^\d{9}$",
        "hkg.national_id.NationalID": r"^[A-Z]{1,2}[0-9]{6}[0-9A]$",
        "irn.national_id.NationalID": r"^\d{3}-?\d{6}-?\d$",
        "isr.national_id.NationalID": r"^(\d{9})$",
        "jpn.national_id.MyNumber": r"^(\d{12}$)",
        "lva.personal_code.PersonalCode": r"^(\d{6}-?\d{5}$)",
        "tur.national_id.NationalID": r"^[1-9]\d{10}$",
        "ukr.entity_id.EntityIDNumber": r"^\d{8}$",
        "ukr.taxpayer_id.TaxpayerIDNumber": r"^\d{10}$",
    }.items()
}

TAX_FILE_KEY = _PACKAGE + "aus.tax_file.TaxFileNumber"
MEDICARE_KEY = _PACKAGE + "aus.medicare.MedicareNumber"


def _classes_by_key():
    return {cls.__module__ + "." + cls.__name__: cls for _, cls in iter_id_classes()}


class TestComputedChecksumGroups(TestCase):
    def test_listed_classes_name_a_checksum_group(self):
        classes = _classes_by_key()
        self.assertEqual(len(COMPUTED_CHECKSUM_GROUP_KEYS), 14)
        for key in COMPUTED_CHECKSUM_GROUP_KEYS:
            with self.subTest(cls=key):
                self.assertIn("checksum", classes[key].METADATA.regexp.groupindex)

    def test_every_computed_checksum_is_the_group_text(self):
        # Guards future classes: a non-bool checksum() result is compared with the `checksum` group by the
        # failure derivation, so the group must cover the check character and hold the computed value.
        checked = set()
        for _, cls in iter_id_classes():
            key = cls.__module__ + "." + cls.__name__
            example = cls.METADATA.example
            computed = cls.checksum(example) if hasattr(cls, "checksum") else None
            if computed is None or isinstance(computed, bool):
                continue
            checked.add(key)
            with self.subTest(cls=key):
                regexp = cls.METADATA.regexp
                self.assertIn("checksum", regexp.groupindex)
                match = util.match_regexp(example, regexp)
                self.assertIsNotNone(match)
                start, end = match.span("checksum")
                self.assertGreaterEqual(start, 0)
                positions = [i for i, char in enumerate(example) if char.isascii() and char.isalnum()]
                self.assertTrue(start <= positions[CHECK_CHARACTER_INDEX.get(key, -1)] < end)
                if key == TAX_FILE_KEY:
                    # checksum() is the weighted-sum remainder (0 means valid), not a check digit, so it
                    # cannot equal the group text of a valid example.
                    self.assertEqual(computed, 0)
                else:
                    self.assertEqual(str(computed), match.group("checksum"))
        self.assertLessEqual(set(COMPUTED_CHECKSUM_GROUP_KEYS), checked)

    def test_tax_file_remainder_is_conservative_when_equal_to_last_digit(self):
        # With 12345678d the weighted sum mod 11 is (2 - d) mod 11 (the last weight, 10, is -1 mod 11), so
        # d=2 is valid, d=1 gives remainder 1 and d=0 gives remainder 2.
        self.assertEqual([AUS.TaxFileNumber.checksum("12345678" + digit) for digit in "210"], [0, 1, 2])
        # Remainder 1 equals the final digit 1: the group cannot prove a mismatch, so the reason stays generic.
        self.assertEqual(failure_reason(AUS.TaxFileNumber, "123456781"), R.VALIDATION_FAILED)
        # Remainder 2 differs from the final digit 0: a definite mismatch.
        self.assertEqual(failure_reason(AUS.TaxFileNumber, "123456780"), R.CHECKSUM_MISMATCH)

    def test_unified_id_code_13_digit_failure_in_the_eik_part_is_generic(self):
        # The checksum group covers only the 13th digit. The first nine digits 123456780 fail the 9-digit check, but
        # the 13th digit is correct for digits 9 to 12 (0123), so no definite mismatch can be shown and the reason
        # stays generic.
        self.assertEqual(failure_reason(BGR.UnifiedIdCode, "1234567801236"), R.VALIDATION_FAILED)
        # A wrong 13th digit is a definite mismatch of the group.
        self.assertEqual(failure_reason(BGR.UnifiedIdCode, "1234567801237"), R.CHECKSUM_MISMATCH)

    def test_medicare_group_is_the_ninth_digit_not_the_issue_digit(self):
        # The check digit is the 9th digit; the issue number and optional /n follow it. For these numbers the
        # computed digit is 0 while the 9th digit is 1.
        for value in ("2123 45671 1", "2123 45671 1/2", "2123-45671-1", "21234567111"):
            with self.subTest(value=value):
                self.assertFalse(AUS.MedicareNumber.validate(value))
                self.assertEqual(failure_reason(AUS.MedicareNumber, value), R.CHECKSUM_MISMATCH)
        # Changing only the issue digit leaves the number valid.
        self.assertTrue(AUS.MedicareNumber.validate("2123 45670 2"))
        self.assertIsNone(failure_reason(AUS.MedicareNumber, "2123 45670 2"))

    def test_chile_lowercase_k_check_character(self):
        # Body 10.000.013: digits from the right 3,1,0,0,0,0,0,1 with weights 2,3,4,5,6,7,2,3 sum to 12,
        # 12 mod 11 = 1, and 11 - 1 = 10, which is written K.
        self.assertEqual(CHL.NationalID.checksum("10.000.013-0"), "K")
        for value in ("10.000.013-K", "10.000.013-k"):
            with self.subTest(value=value):
                self.assertTrue(CHL.NationalID.validate(value))
                self.assertIsNone(failure_reason(CHL.NationalID, value))
        self.assertEqual(failure_reason(CHL.NationalID, "10.000.013-0"), R.CHECKSUM_MISMATCH)
        # A lowercase k that is wrong for its body is a definite mismatch too.
        self.assertNotEqual(CHL.NationalID.checksum("10.000.014-0"), "K")
        self.assertEqual(failure_reason(CHL.NationalID, "10.000.014-k"), R.CHECKSUM_MISMATCH)

    def test_group_refactor_matches_the_old_patterns(self):
        classes = _classes_by_key()
        self.assertEqual(set(OLD_PATTERNS), set(COMPUTED_CHECKSUM_GROUP_KEYS))
        for key, old in OLD_PATTERNS.items():
            cls = classes[key]
            old_regexp = re.compile(old)
            new_regexp = cls.METADATA.regexp
            corpus = self.corpus(key, cls)
            self.assertGreater(len(corpus), 500)
            self.assertTrue(any(old_regexp.fullmatch(value) for value in corpus))
            with self.subTest(cls=key):
                for value in corpus:
                    self.assertEqual(
                        old_regexp.fullmatch(value) is not None, new_regexp.fullmatch(value) is not None, repr(value)
                    )

    @staticmethod
    def corpus(key, cls):
        """Deterministic inputs: the example, expanded masks and single-edit neighbours of each."""
        alphabet = "0123456789 -./AKkXZ\n\u0663"
        digits = "1234567890"
        bases = {cls.METADATA.example}
        for mask in cls.METADATA.masks:
            for letter in ("7", "K", "k"):
                text = mask.replace("X", letter).replace("L", "A").replace("C", letter)
                out = []
                for char in text:
                    out.append(digits[len(out) % len(digits)] if char == "#" else char)
                bases.add("".join(out))
        if key == MEDICARE_KEY:
            for head in ("2123 45670 1", "2123-45670-1", "2123456701", "212345670"):
                for suffix in ("", "1", "2", "/", "/2", "-2", " 2", "/22", " 2 2", "-2-2"):
                    bases.add(head + suffix)
        values = set(bases)
        for base in bases:
            for index in range(len(base) + 1):
                if index < len(base):
                    values.add(base[:index] + base[index + 1 :])
                for char in alphabet:
                    values.add(base[:index] + char + base[index:])
                    if index < len(base):
                        values.add(base[:index] + char + base[index + 1 :])
        return sorted(values)
