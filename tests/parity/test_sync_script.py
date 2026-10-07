"""
`scripts/sync_parity_corpus.py` reports an unusable corpus with exit code 2 and no traceback.

`--check` uses exit code 1 for "out of date", so a corrupt corpus must not look like that. The script runs in a
temporary copy of the files it needs, so the checkout is never touched.
"""
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import List, Tuple
from unittest import TestCase, main

ROOT = Path(__file__).resolve().parent.parent.parent
COPIED_FILES = [
    "scripts/sync_parity_corpus.py",
    "tests/__init__.py",
    "tests/parity/__init__.py",
    "tests/parity/corpus.py",
    "tests/parity/corpus.json",
    "tests/parity/expected_python.json",
]


class SyncScriptTest(TestCase):
    def setUp(self) -> None:
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.parent = Path(directory.name)
        self.copy = self.parent / "checkout"
        for relative in COPIED_FILES:
            target = self.copy / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(ROOT / relative, target)
        shutil.copytree(ROOT / "idnumbers", self.copy / "idnumbers", ignore=shutil.ignore_patterns("__pycache__"))

    def run_script(self, *arguments: str) -> Tuple[int, str, str]:
        run = subprocess.run(
            [sys.executable, str(self.copy / "scripts" / "sync_parity_corpus.py")] + list(arguments),
            cwd=str(self.parent), stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True,
        )
        return run.returncode, run.stdout, run.stderr

    def write_corpus(self, text: str) -> None:
        (self.copy / "tests" / "parity" / "corpus.json").write_text(text, encoding="utf-8")

    def assert_exit_2_without_traceback(self, arguments: List[str]) -> str:
        code, _, stderr = self.run_script(*arguments)
        self.assertEqual(2, code, stderr)
        self.assertNotIn("Traceback", stderr)
        self.assertIn("sync_parity_corpus.py:", stderr)
        return stderr

    def test_check_passes_on_the_committed_record(self) -> None:
        code, stdout, stderr = self.run_script("--check")
        self.assertEqual(0, code, stdout + stderr)

    def test_corrupt_corpus_exits_2(self) -> None:
        self.write_corpus("{bad")
        self.assert_exit_2_without_traceback(["--check"])

    def test_non_string_seed_exits_2(self) -> None:
        self.write_corpus('{"ALB": [1]}')
        self.assert_exit_2_without_traceback(["--check"])

    def test_unknown_country_exits_2(self) -> None:
        self.write_corpus('{"XXX": ["1"]}')
        stderr = self.assert_exit_2_without_traceback(["--check"])
        self.assertIn("XXX", stderr)

    def test_regeneration_also_exits_2_and_writes_nothing(self) -> None:
        self.write_corpus("{bad")
        record = self.copy / "tests" / "parity" / "expected_python.json"
        before = record.read_bytes()
        self.assert_exit_2_without_traceback([])
        self.assertEqual(before, record.read_bytes())


if __name__ == "__main__":
    main()
