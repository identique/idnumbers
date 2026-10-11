"""
`scripts/sync_parity_corpus.py` reports an unusable corpus with exit code 2 and no traceback.

`--check` uses exit code 1 for "out of date", so a corrupt corpus must not look like that. The script runs in a
temporary copy of the files it needs, so the checkout is never touched.

`--from-port` is exercised against a scratch git repository built in the temporary directory, never against a real
port checkout.
"""
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Dict, List, Tuple
from unittest import TestCase, main, skipIf

ROOT = Path(__file__).resolve().parent.parent.parent
COPIED_FILES = [
    "scripts/sync_parity_corpus.py",
    "tests/__init__.py",
    "tests/parity/__init__.py",
    "tests/parity/corpus.py",
    "tests/parity/corpus.json",
    "tests/parity/expected_python.json",
]
TRACKED_FILES = [
    "tests/parity/corpus.json",
    "tests/parity/corpus.py",
    "tests/parity/expected_python.json",
]
COPIED_MESSAGE = "corpus: copied"


def hermetic_git_environment(home: Path) -> Dict[str, str]:
    """An environment in which git ignores the machine's and the user's configuration (signing, hooks, aliases)."""
    home.mkdir(parents=True, exist_ok=True)
    environment = {name: value for name, value in os.environ.items() if not name.startswith("GIT_")}
    environment.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull, HOME=str(home), USERPROFILE=str(home))
    return environment


class CheckoutCase(TestCase):
    """A temporary copy of the files the script needs, and a way to run the script in it."""

    environment: Dict[str, str]

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
        self.environment = hermetic_git_environment(self.parent / "home")

    def run_script(self, *arguments: str) -> Tuple[int, str, str]:
        run = subprocess.run(
            [sys.executable, str(self.copy / "scripts" / "sync_parity_corpus.py")] + list(arguments),
            cwd=str(self.parent), stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True,
            env=self.environment,
        )
        return run.returncode, run.stdout, run.stderr

    def tracked_bytes(self) -> Dict[str, bytes]:
        """The three files `--from-port` may write, as bytes, for before and after comparisons."""
        return {relative: (self.copy / relative).read_bytes() for relative in TRACKED_FILES}

    def assert_exit_2_without_traceback(self, arguments: List[str]) -> str:
        code, stdout, stderr = self.run_script(*arguments)
        self.assertEqual(2, code, stderr)
        self.assertNotIn("Traceback", stderr)
        self.assertIn("sync_parity_corpus.py:", stderr)
        self.assertNotIn(COPIED_MESSAGE, stdout)
        return stderr

    def write_corpus(self, text: str) -> None:
        (self.copy / "tests" / "parity" / "corpus.json").write_text(text, encoding="utf-8")


class SyncScriptTest(CheckoutCase):
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


@skipIf(shutil.which("git") is None, "git is not on PATH; the scratch port repository cannot be built")
class FromPortTest(CheckoutCase):
    """`--from-port` against a scratch git repository standing in for the Node port."""

    # A seed that Python accepts; any country whose class loads would do.
    PORT_CORPUS = '{"ALB": ["J50101001A"]}\n'

    def setUp(self) -> None:
        super().setUp()
        self.port = self.parent / "port"
        self.port.mkdir()
        self.git("init", "--quiet")

    def git(self, *arguments: str) -> str:
        """Run git in the scratch port, ignoring every configuration file and hook of the machine."""
        command = [
            "git", "-C", str(self.port), "-c", "user.name=Port Test", "-c", "user.email=port@example.invalid",
            "-c", "commit.gpgsign=false", "-c", "core.hooksPath=%s" % os.devnull, "-c", "init.defaultBranch=main",
        ] + list(arguments)
        run = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True,
                             env=self.environment)
        self.assertEqual(0, run.returncode, "%s: %s" % (" ".join(arguments), run.stderr))
        return run.stdout.strip()

    def commit_port_corpus(self, text: str) -> str:
        """Commit `parity/corpus.json` with this text to the scratch port and return the new HEAD."""
        corpus = self.port / "parity" / "corpus.json"
        corpus.parent.mkdir(exist_ok=True)
        corpus.write_text(text, encoding="utf-8")
        self.git("add", "parity/corpus.json")
        self.git("commit", "--quiet", "-m", "corpus")
        return self.git("rev-parse", "HEAD")

    def test_failed_regeneration_restores_the_tree_and_reports_nothing_copied(self) -> None:
        # The class loads, so the port's corpus passes validation and is copied; the regeneration then fails
        # because validate() raises, which the library contract forbids.
        alb = self.copy / "idnumbers" / "nationalid" / "ALB.py"
        alb.write_text(
            alb.read_text(encoding="utf-8")
            + "\n\ndef _raise(value):\n    raise RuntimeError('sabotaged')\n\n\n"
            + "NationalID.validate = staticmethod(_raise)\n",
            encoding="utf-8",
        )
        self.commit_port_corpus(self.PORT_CORPUS)
        before = self.tracked_bytes()
        code, stdout, stderr = self.run_script("--from-port", str(self.port))
        self.assertEqual(2, code, stdout + stderr)
        self.assertIn("sabotaged", stderr)
        self.assertNotIn("Traceback", stderr)
        self.assertNotIn(COPIED_MESSAGE, stdout)
        self.assertEqual(before, self.tracked_bytes())

    def test_write_error_while_copying_restores_the_tree(self) -> None:
        # The corpus is written first and the read-only module second, so the copy fails half-way.
        module = self.copy / "tests" / "parity" / "corpus.py"
        module.chmod(0o444)
        self.addCleanup(module.chmod, 0o644)
        try:
            with open(str(module), "ab"):
                self.skipTest("the file system does not enforce read-only files (running as root?)")
        except OSError:
            pass
        self.commit_port_corpus(self.PORT_CORPUS)
        before = self.tracked_bytes()
        code, stdout, stderr = self.run_script("--from-port", str(self.port))
        self.assertEqual(2, code, stdout + stderr)
        self.assertNotIn("Traceback", stderr)
        self.assertNotIn(COPIED_MESSAGE, stdout)
        self.assertEqual(before, self.tracked_bytes())


if __name__ == "__main__":
    main()
