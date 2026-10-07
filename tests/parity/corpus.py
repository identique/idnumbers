"""
The cross-implementation parity corpus, and Python's own recorded validity for it.

The Node.js/TypeScript port (`identique/idnumbers-npm <https://github.com/identique/idnumbers-npm>`_, MIT) keeps a
differential parity harness: `parity/corpus.json` maps 78 countries to seed inputs, and the harness expands every seed
into neighbouring test vectors and compares the two libraries' validity. This module vendors that corpus and records
which of the expanded vectors *this* library accepts (`tests/parity/expected_python.json`), so that a change of Python
validity on any shared vector fails `tests/parity/test_corpus.py` and prompts a note on the port (AGENTS.md, "Fixing
an issue", step 4).

The corpus is pinned to port commit `PORT_COMMIT`. The vector expansion and the country-to-class mapping mirror the
port's helpers at that commit and must stay equal to them:

- expansion: https://github.com/identique/idnumbers-npm/blob/694a9cc56615813603e554e5b19071b750b2362d/scripts/parity/check-parity.mjs
- class mapping: https://github.com/identique/idnumbers-npm/blob/694a9cc56615813603e554e5b19071b750b2362d/scripts/parity/python_validity.py
- documentation: https://github.com/identique/idnumbers-npm/blob/694a9cc56615813603e554e5b19071b750b2362d/docs/PARITY.md

The port's own check compares validity with an allowlist pinned to an older Python commit, so it is not run here.
Refresh the vendored corpus and the golden results with `python3 scripts/sync_parity_corpus.py`.

Unlike the port's helper, an exception raised by `validate()` is an error here, not "invalid": `validate()` never
raises (AGENTS.md, "Input contract").
"""
import hashlib
import importlib
import json
import re
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional

PORT_REPOSITORY = "identique/idnumbers-npm"
PORT_COMMIT = "694a9cc56615813603e554e5b19071b750b2362d"
CORPUS_RELATIVE_PATH = "parity/corpus.json"

CORPUS_PATH = Path(__file__).with_name("corpus.json")
EXPECTED_PATH = Path(__file__).with_name("expected_python.json")

# The port's `SEPARATORS = /[\s.\-/()]/g`. `\s` is spelled out because JavaScript's whitespace set differs from
# Python's `re` one (for example U+FEFF is whitespace in JavaScript only).
SEPARATORS = re.compile("[\t\n\v\f\r    -     　﻿.\\-/()]")

# Countries whose compared class is not `<CODE>:NationalID`, as "module:Class" relative to `idnumbers.nationalid`.
# An input is valid when any class accepts it.
CLASS_OVERRIDES: Dict[str, List[str]] = {
    # Python's AUS.NationalID aliases the driver licence; the port registers Medicare.
    "AUS": ["aus.medicare:MedicareNumber"],
    # Python's GRC.NationalID aliases the identity card; the port registers the tax ID.
    "GRC": ["grc.tax_id:TaxIdentityNumber"],
    # The port registers each of these as a union of the current and the old format.
    "BGD": ["BGD:NationalID", "BGD:OldNationalID"],
    "LKA": ["LKA:NationalID", "LKA:OldNationalID"],
    # The port registers the social security and the tax registration numbers together.
    "SMR": ["SMR:SocialSecurityNumber", "SMR:TaxRegistrationNumber"],
}


class ContractViolation(AssertionError):
    """A `validate()` that raised or returned a non-bool, which AGENTS.md forbids."""


def load_corpus() -> Dict[str, List[str]]:
    """The vendored seed corpus: country code to its sorted seed inputs."""
    data = json.loads(CORPUS_PATH.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("%s: expected a JSON object" % CORPUS_PATH)
    corpus: Dict[str, List[str]] = {}
    for code, seeds in data.items():
        if not isinstance(seeds, list) or not all(isinstance(seed, str) for seed in seeds):
            raise ValueError("%s: %s must be a list of strings" % (CORPUS_PATH, code))
        corpus[code] = list(seeds)
    return corpus


def corpus_sha256() -> str:
    """SHA-256 of the vendored corpus file, as bytes on disk."""
    return hashlib.sha256(CORPUS_PATH.read_bytes()).hexdigest()


def bump_character(char: str) -> Optional[str]:
    """The next ASCII digit or letter (wrapping 9 to 0, Z to A, z to a), or None for any other character."""
    if "0" <= char <= "9":
        return str((int(char) + 1) % 10)
    if "A" <= char <= "Z":
        return chr((ord(char) - 65 + 1) % 26 + 65)
    if "a" <= char <= "z":
        return chr((ord(char) - 97 + 1) % 26 + 97)
    return None


def neighbourhood(seed: str) -> Iterator[str]:
    """The seed plus its neighbours: compact form, each character bumped, truncated, extended."""
    yield seed
    yield SEPARATORS.sub("", seed)
    for index, char in enumerate(seed):
        bumped = bump_character(char)
        if bumped is not None:
            yield seed[:index] + bumped + seed[index + 1:]
    if len(seed) > 1:
        yield seed[:-1]
    yield seed + "0"


def expand_corpus(corpus: Dict[str, List[str]]) -> Dict[str, List[str]]:
    """Vectors per country, deduplicated and in first-occurrence order."""
    expanded: Dict[str, List[str]] = {}
    for code, seeds in corpus.items():
        vectors: Dict[str, None] = {}
        for seed in seeds:
            for vector in neighbourhood(seed):
                vectors.setdefault(vector, None)
        expanded[code] = list(vectors)
    return expanded


def class_specs(code: str) -> List[str]:
    """The "module:Class" specs, relative to `idnumbers.nationalid`, that are compared for a country."""
    return list(CLASS_OVERRIDES.get(code, ["%s:NationalID" % code]))


def load_classes(code: str) -> List[type]:
    """Import the compared classes of a country; a missing module or class raises."""
    classes: List[type] = []
    for spec in class_specs(code):
        module_name, class_name = spec.split(":")
        module = importlib.import_module("idnumbers.nationalid.%s" % module_name)
        cls = getattr(module, class_name)
        classes.append(cls)
    return classes


def _accepts(cls: Any, code: str, vector: str) -> bool:
    name = "%s.%s" % (cls.__module__, cls.__name__)
    try:
        result = cls.validate(vector)
    except Exception as error:
        raise ContractViolation(
            "%s (%s): validate(%r) raised %s: %s; validate() must never raise"
            % (code, name, vector, type(error).__name__, error)
        ) from error
    if not isinstance(result, bool):
        raise ContractViolation(
            "%s (%s): validate(%r) returned %r, not a bool" % (code, name, vector, result)
        )
    return result


def python_valid(code: str, vectors: List[str]) -> List[str]:
    """The vectors that any compared class of the country validates, in input order.

    Every class sees every vector, so a contract violation of any of them is reported.
    """
    classes = load_classes(code)
    accepted: List[str] = []
    for vector in vectors:
        results = [_accepts(cls, code, vector) for cls in classes]
        if any(results):
            accepted.append(vector)
    return accepted


def build_expected() -> Dict[str, Any]:
    """The golden record: corpus provenance, expansion size, compared classes and Python-valid vectors."""
    expanded = expand_corpus(load_corpus())
    return {
        "corpus": {
            "repository": PORT_REPOSITORY,
            "commit": PORT_COMMIT,
            "path": CORPUS_RELATIVE_PATH,
            "sha256": corpus_sha256(),
        },
        "vectors": sum(len(vectors) for vectors in expanded.values()),
        "classes": {code: class_specs(code) for code in expanded},
        "valid": {code: sorted(python_valid(code, vectors)) for code, vectors in expanded.items()},
    }


def render_expected(expected: Dict[str, Any]) -> str:
    """Deterministic, ASCII-only JSON text of a golden record."""
    return json.dumps(expected, indent=2, sort_keys=True, ensure_ascii=True) + "\n"
