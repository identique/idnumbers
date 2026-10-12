"""
Python's validity on the Node port's parity corpus must not change silently.

`tests/parity/expected_python.json` records which expanded corpus vectors this library accepts. A change that alters
validity on a vector the port shares fails `test_python_validity_matches_the_golden_record`, so the change gets a
note on identique/idnumbers-npm.
See `tests/parity/corpus.py` for the provenance and `python3 scripts/sync_parity_corpus.py` for the refresh.
"""

import json
from typing import Any, Dict, List
from unittest import TestCase, main
from unittest.mock import patch

from tests.parity import corpus

# The vector count the port documents for this corpus: "78 countries, 17960 vectors" in docs/PARITY.md at the pinned
# port commit. The Python expansion must reproduce it, which shows that both sides expand the seeds identically.
# After `scripts/sync_parity_corpus.py --from-port` pins a newer port commit, update both numbers to the ones that
# commit's docs/PARITY.md documents.
PORT_DOCUMENTED_VECTORS = 17960
PORT_DOCUMENTED_COUNTRIES = 78

LISTED_LIMIT = 20

CHANGED_MESSAGE = (
    "Python validity changed on the shared parity corpus. If intended, regenerate with "
    "`python3 scripts/sync_parity_corpus.py` and note the change on identique/idnumbers-npm "
    "(AGENTS.md, Fixing an issue, step 4)."
)


def _load_expected() -> Dict[str, Any]:
    data = json.loads(corpus.EXPECTED_PATH.read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    return data


def _listed(vectors: List[str]) -> str:
    shown = vectors[:LISTED_LIMIT]
    more = len(vectors) - len(shown)
    text = ", ".join(repr(vector) for vector in shown) or "none"
    return text + (" ... and %d more" % more if more > 0 else "")


class ParityCorpusTest(TestCase):
    expected: Dict[str, Any]
    seeds: Dict[str, List[str]]
    expanded: Dict[str, List[str]]

    @classmethod
    def setUpClass(cls) -> None:
        cls.expected = _load_expected()
        cls.seeds = corpus.load_corpus()
        cls.expanded = corpus.expand_corpus(cls.seeds)

    def test_vendored_corpus_matches_recorded_provenance(self) -> None:
        provenance = self.expected["corpus"]
        self.assertEqual(corpus.PORT_REPOSITORY, provenance["repository"])
        self.assertEqual(corpus.PORT_COMMIT, provenance["commit"])
        self.assertEqual(corpus.CORPUS_RELATIVE_PATH, provenance["path"])
        self.assertEqual(
            provenance["sha256"],
            corpus.corpus_sha256(),
            "tests/parity/corpus.json changed without regenerating tests/parity/expected_python.json; "
            "run `python3 scripts/sync_parity_corpus.py`",
        )

    def test_vendored_corpus_is_sorted_and_unique(self) -> None:
        self.assertEqual(sorted(self.seeds), list(self.seeds), "country keys are not sorted")
        for code, seeds in self.seeds.items():
            with self.subTest(country=code):
                self.assertTrue(seeds, "no seeds")
                self.assertEqual(sorted(set(seeds)), seeds, "seeds are not sorted and unique")

    def test_expansion_matches_the_port(self) -> None:
        total = sum(len(vectors) for vectors in self.expanded.values())
        self.assertEqual(PORT_DOCUMENTED_COUNTRIES, len(self.expanded))
        self.assertEqual(PORT_DOCUMENTED_VECTORS, total)
        self.assertEqual(self.expected["vectors"], total)
        for code, vectors in self.expanded.items():
            with self.subTest(country=code):
                self.assertEqual(len(vectors), len(set(vectors)), "duplicate vectors")

    def test_compared_classes_load_and_match_the_record(self) -> None:
        recorded = self.expected["classes"]
        self.assertEqual(sorted(self.expanded), sorted(recorded))
        for code in self.expanded:
            with self.subTest(country=code):
                self.assertEqual(recorded[code], corpus.class_specs(code))
                classes = corpus.load_classes(code)
                self.assertEqual(len(recorded[code]), len(classes))
                for cls in classes:
                    self.assertTrue(callable(getattr(cls, "validate", None)), "%r has no validate()" % cls)

    def test_python_validity_matches_the_golden_record(self) -> None:
        for code, vectors in self.expanded.items():
            with self.subTest(country=code):
                recorded = set(self.expected["valid"][code])
                self.assertLessEqual(recorded, set(vectors), "the record holds vectors outside the corpus")
                accepted = corpus.python_valid(code, vectors)
                accepted_set = set(accepted)
                newly_valid = [vector for vector in accepted if vector not in recorded]
                newly_invalid = [vector for vector in vectors if vector in recorded and vector not in accepted_set]
                if newly_valid or newly_invalid:
                    self.fail(
                        "%s\n%s: %d newly valid: %s\n%s: %d newly invalid: %s"
                        % (
                            CHANGED_MESSAGE,
                            code,
                            len(newly_valid),
                            _listed(newly_valid),
                            code,
                            len(newly_invalid),
                            _listed(newly_invalid),
                        )
                    )

    def test_record_and_corpus_cover_the_same_countries(self) -> None:
        recorded = set(self.expected["valid"])
        self.assertEqual(set(), recorded - set(self.seeds), "recorded but not in the corpus")
        self.assertEqual(set(), set(self.seeds) - recorded, "in the corpus but not recorded")
        self.assertEqual(set(self.expected["classes"]), recorded)


class ContractViolationTest(TestCase):
    """A validate() that raises or returns a non-bool is an error that names the country and the compared class."""

    def test_raising_validate_names_the_country_and_the_spec(self) -> None:
        from idnumbers.nationalid import CHN

        def explode(value: str) -> bool:
            raise RuntimeError("boom")

        with patch.object(CHN.NationalID, "validate", staticmethod(explode)):
            with self.assertRaises(corpus.ContractViolation) as caught:
                corpus.python_valid("CHN", ["110101199003078515"])
        message = str(caught.exception)
        self.assertIn("CHN (CHN:NationalID)", message)
        self.assertIn("RuntimeError: boom", message)
        self.assertNotIn("AliasType", message)

    def test_non_bool_validate_names_the_overridden_class_spec(self) -> None:
        from idnumbers.nationalid.aus.medicare import MedicareNumber

        def not_a_bool(value: str) -> Any:
            return 1

        with patch.object(MedicareNumber, "validate", staticmethod(not_a_bool)):
            with self.assertRaises(corpus.ContractViolation) as caught:
                corpus.python_valid("AUS", ["2123456701"])
        message = str(caught.exception)
        self.assertIn("AUS (aus.medicare:MedicareNumber)", message)
        self.assertIn("returned 1, not a bool", message)

    def test_every_class_of_a_country_sees_every_vector(self) -> None:
        from idnumbers.nationalid import SMR

        def explode(value: str) -> bool:
            raise RuntimeError("boom")

        with patch.object(SMR.TaxRegistrationNumber, "validate", staticmethod(explode)):
            with self.assertRaises(corpus.ContractViolation) as caught:
                corpus.python_valid("SMR", ["12345"])
        self.assertIn("SMR (SMR:TaxRegistrationNumber)", str(caught.exception))


if __name__ == "__main__":
    main()
