#!/usr/bin/env python3
"""
Refresh the parity corpus and Python's golden validity record under tests/parity/.

The Node.js port's differential parity corpus is vendored in `tests/parity/corpus.json`, and
`tests/parity/expected_python.json` records which of its expanded vectors this checkout accepts (see
`tests/parity/corpus.py`). `tests/parity/test_corpus.py` fails when Python validity on those vectors changes.

Usage, from anywhere (standard library only, Python 3.9 or newer):

    python3 scripts/sync_parity_corpus.py
        Regenerate tests/parity/expected_python.json from this checkout and print a summary. Run it after an
        intended validity change, then list the changed vectors in the note on identique/idnumbers-npm.

    python3 scripts/sync_parity_corpus.py --check
        Write nothing. Exit 1 if the regenerated file would differ from the committed one.

    python3 scripts/sync_parity_corpus.py --from-port <port checkout>
        First copy <port checkout>/parity/corpus.json into tests/parity/corpus.json and pin PORT_COMMIT in
        tests/parity/corpus.py to the checkout's HEAD (the checkout is only read and must be clean), then
        regenerate as above.
        If the port's corpus changed, also update the vector and country counts pinned in
        tests/parity/test_corpus.py to the numbers in the port's docs/PARITY.md.

Exit codes: 0 success, 1 `--check` found differences, 2 the script could not run (bad checkout, wrong `idnumbers`
import, a corpus that is corrupt, has non-string seeds or names a country without a class, or a validate() that
raised, which the library contract forbids). A failed run never leaves a half-updated tree: `--from-port` validates
the port's corpus before writing and restores the previous files if regeneration fails.
"""
import argparse
import importlib
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

REPOSITORY_ROOT = Path(__file__).resolve().parent.parent

PORT_COMMIT_LINE = re.compile(r'^PORT_COMMIT = "[0-9a-f]{40}"$')


class SetupError(Exception):
    """The script cannot do what was asked; reported with exit code 2."""


def import_corpus_module() -> Any:
    """Import tests.parity.corpus and idnumbers from this checkout, never from site-packages."""
    sys.path.insert(0, str(REPOSITORY_ROOT))
    idnumbers = importlib.import_module("idnumbers")
    loaded_from = Path(str(idnumbers.__file__)).resolve()
    if REPOSITORY_ROOT not in loaded_from.parents:
        raise SetupError("imported idnumbers from %s, not from this checkout (%s)" % (loaded_from, REPOSITORY_ROOT))
    try:
        return importlib.import_module("tests.parity.corpus")
    except ImportError as error:
        raise SetupError("cannot import tests.parity.corpus from %s: %s" % (REPOSITORY_ROOT, error))


def git_output(port: Path, *arguments: str) -> str:
    try:
        run = subprocess.run(
            ["git", "-C", str(port)] + list(arguments),
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True,
        )
    except OSError as error:
        raise SetupError("cannot run git: %s" % error)
    if run.returncode != 0:
        raise SetupError("git %s failed in %s: %s" % (" ".join(arguments), port, run.stderr.strip()))
    return run.stdout


def read_port(port: Path) -> Tuple[bytes, str]:
    """The corpus bytes and the HEAD commit of a clean port checkout."""
    source = port / "parity" / "corpus.json"
    if not source.is_file():
        raise SetupError("%s does not exist; --from-port needs a checkout of identique/idnumbers-npm" % source)
    commit = git_output(port, "rev-parse", "HEAD").strip()
    if not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise SetupError("unexpected HEAD %r in %s" % (commit, port))
    dirty = git_output(port, "status", "--porcelain")
    if dirty.strip():
        raise SetupError("%s has uncommitted changes; refusing to pin a corpus that is not at %s:\n%s"
                         % (port, commit, dirty.rstrip()))
    return source.read_bytes(), commit


def pin_commit(corpus_module: Path, commit: str) -> str:
    """The text of tests/parity/corpus.py with the PORT_COMMIT line replaced; the line must exist exactly once."""
    lines = corpus_module.read_text(encoding="utf-8").splitlines(keepends=True)
    indexes = [index for index, line in enumerate(lines) if PORT_COMMIT_LINE.match(line.rstrip("\r\n"))]
    if len(indexes) != 1:
        raise SetupError('expected exactly one `PORT_COMMIT = "<40 hex digits>"` line in %s, found %d'
                         % (corpus_module, len(indexes)))
    lines[indexes[0]] = 'PORT_COMMIT = "%s"\n' % commit
    return "".join(lines)


def check_corpus_data(corpus: Any, parsed: Any, source: str) -> None:
    """Fail unless the data is a JSON object of country code to list of strings and every country's classes load."""
    if not isinstance(parsed, dict):
        raise SetupError("%s: expected a JSON object" % source)
    for code, seeds in parsed.items():
        if not isinstance(seeds, list) or not all(isinstance(seed, str) for seed in seeds):
            raise SetupError("%s: %s must be a list of strings" % (source, code))
        for spec in corpus.class_specs(code):
            module_name, class_name = spec.split(":")
            try:
                module = importlib.import_module("idnumbers.nationalid.%s" % module_name)
                getattr(module, class_name)
            except (ImportError, AttributeError, ValueError) as error:
                raise SetupError("%s: cannot load the Python class for %r (%s): %s" % (source, code, spec, error))


def copy_from_port(port: Path, corpus: Any) -> Any:
    """Vendor the port's corpus and commit pin, then reload the corpus module so it sees both.

    Everything is validated before the first write, so a bad port corpus leaves the tree untouched.
    """
    data, commit = read_port(port)
    source = "%s/parity/corpus.json" % port
    try:
        parsed = json.loads(data.decode("utf-8"))
    except ValueError as error:
        raise SetupError("%s is not valid JSON: %s" % (source, error))
    check_corpus_data(corpus, parsed, source)
    module_path = Path(corpus.__file__)
    pinned = pin_commit(module_path, commit)
    corpus.CORPUS_PATH.write_bytes(data)
    module_path.write_bytes(pinned.encode("utf-8"))
    print("corpus: copied parity/corpus.json from %s at %s" % (port, commit))
    return importlib.reload(corpus)


def read_previous(path: Path) -> Optional[Dict[str, Any]]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return data if isinstance(data, dict) else None


def changed_vectors(previous: Optional[Dict[str, Any]], current: Dict[str, Any]) -> Dict[str, List[str]]:
    """Per country, the vectors whose validity differs from the previous record (all valid ones if none)."""
    old: Dict[str, Any] = previous.get("valid", {}) if previous else {}
    changes: Dict[str, List[str]] = {}
    for code in sorted(set(old) | set(current["valid"])):
        before: Set[str] = set(old.get(code, []))
        after: Set[str] = set(current["valid"].get(code, []))
        difference = sorted(before ^ after)
        if difference:
            changes[code] = difference
    return changes


def summary(current: Dict[str, Any], changes: Dict[str, List[str]]) -> str:
    valid = sum(len(vectors) for vectors in current["valid"].values())
    changed = sum(len(vectors) for vectors in changes.values())
    return "%d countries, %d vectors, %d Python-valid, %d changed validity vs the previous record" % (
        len(current["valid"]), current["vectors"], valid, changed)


def describe_changes(changes: Dict[str, List[str]], limit: int = 20) -> List[str]:
    lines: List[str] = []
    for code, vectors in changes.items():
        shown = ", ".join(repr(vector) for vector in vectors[:limit])
        more = len(vectors) - limit
        lines.append("  %s: %d changed: %s%s" % (code, len(vectors), shown, " ... and %d more" % more if more > 0 else ""))
    return lines


def parse_arguments(argv: Optional[List[str]]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Refresh tests/parity/ (see the module docstring).")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true",
                      help="write nothing; exit 1 if tests/parity/expected_python.json is out of date")
    mode.add_argument("--from-port", metavar="PATH", type=Path,
                      help="first vendor PATH/parity/corpus.json and pin PATH's HEAD commit (PATH must be clean)")
    return parser.parse_args(argv)


def restore(snapshot: Dict[Path, bytes]) -> None:
    for path, content in snapshot.items():
        path.write_bytes(content)


def run(arguments: argparse.Namespace) -> int:
    corpus = import_corpus_module()
    snapshot: Dict[Path, bytes] = {}
    if arguments.from_port is not None:
        snapshot = {path: path.read_bytes() for path in (corpus.CORPUS_PATH, Path(corpus.__file__))}
        corpus = copy_from_port(arguments.from_port.resolve(), corpus)
    try:
        return regenerate(arguments, corpus)
    except BaseException:
        # A failure after --from-port wrote the corpus must not leave a half-updated tree.
        restore(snapshot)
        raise


def regenerate(arguments: argparse.Namespace, corpus: Any) -> int:
    previous = read_previous(corpus.EXPECTED_PATH)
    try:
        current = corpus.build_expected()
    except corpus.ContractViolation as error:
        raise SetupError(str(error))
    except (OSError, ValueError, ImportError, AttributeError) as error:
        raise SetupError("cannot build the record from tests/parity/corpus.json: %s: %s"
                         % (type(error).__name__, error))
    text = corpus.render_expected(current)
    changes = changed_vectors(previous, current)
    print(summary(current, changes))

    expected_path: Path = corpus.EXPECTED_PATH
    existing = expected_path.read_bytes() if expected_path.is_file() else None
    if arguments.check:
        if existing == text.encode("utf-8"):
            print("%s is up to date" % expected_path.relative_to(REPOSITORY_ROOT))
            return 0
        print("%s is out of date; run `python3 scripts/sync_parity_corpus.py`"
              % expected_path.relative_to(REPOSITORY_ROOT))
        print("\n".join(describe_changes(changes)))
        return 1

    expected_path.write_bytes(text.encode("utf-8"))
    print("wrote %s" % expected_path.relative_to(REPOSITORY_ROOT))
    if changes:
        print("Note these changes on identique/idnumbers-npm (AGENTS.md, Fixing an issue, step 4):")
        print("\n".join(describe_changes(changes)))
    return 0


def main(argv: Optional[List[str]] = None) -> int:
    arguments = parse_arguments(argv)
    try:
        return run(arguments)
    except SetupError as error:
        print("sync_parity_corpus.py: %s" % error, file=sys.stderr)
        return 2
    except OSError as error:
        print("sync_parity_corpus.py: %s" % error, file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
