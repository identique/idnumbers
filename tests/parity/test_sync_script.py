"""
`scripts/sync_parity_corpus.py` reports an unusable corpus with exit code 2 and no traceback.

`--check` uses exit code 1 for "out of date", so a corrupt corpus must not look like that. The script runs in a
temporary copy of the files it needs, so the checkout is never touched.

`--from-port` is exercised against a scratch git repository built in the temporary directory, never against a real
port checkout.
"""
import contextlib
import importlib.util
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import types
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple
from unittest import TestCase, main, mock, skipIf

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


def load_script() -> Any:
    """Import `scripts/sync_parity_corpus.py` as a private module, for in-process tests of its functions.

    Importing it only defines names. It changes `sys.path` solely inside `import_corpus_module()`, which these tests
    always replace, so loading it is harmless.
    """
    spec = importlib.util.spec_from_file_location(
        "sync_parity_corpus_under_test", str(ROOT / "scripts" / "sync_parity_corpus.py"))
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


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
        corpus.write_bytes(text.encode("utf-8"))
        self.git("add", "parity/corpus.json")
        self.git("commit", "--quiet", "-m", "corpus")
        return self.git("rev-parse", "HEAD")

    def pinned_commit(self) -> str:
        text = (self.copy / "tests" / "parity" / "corpus.py").read_text(encoding="utf-8")
        match = re.search(r'^PORT_COMMIT = "([0-9a-f]{40})"$', text, re.MULTILINE)
        self.assertIsNotNone(match)
        assert match is not None
        return match.group(1)

    def assert_refused(self, expected_message: str) -> None:
        before = self.tracked_bytes()
        stderr = self.assert_exit_2_without_traceback(["--from-port", str(self.port)])
        self.assertIn(expected_message, stderr)
        self.assertEqual(before, self.tracked_bytes())

    def test_dirty_port_with_an_untracked_file_is_refused(self) -> None:
        self.commit_port_corpus(self.PORT_CORPUS)
        (self.port / "scratch.txt").write_text("untracked\n", encoding="utf-8")
        self.assert_refused("uncommitted changes")

    def test_dirty_port_with_a_modified_corpus_is_refused(self) -> None:
        self.commit_port_corpus(self.PORT_CORPUS)
        (self.port / "parity" / "corpus.json").write_text('{"ALB": ["J50101001A", "J50101031R"]}\n', encoding="utf-8")
        self.assert_refused("uncommitted changes")

    def test_port_without_a_corpus_is_refused(self) -> None:
        self.assert_refused("does not exist")

    def test_port_that_is_not_a_git_checkout_is_refused(self) -> None:
        shutil.rmtree(str(self.port / ".git"))
        (self.port / "parity").mkdir()
        (self.port / "parity" / "corpus.json").write_text(self.PORT_CORPUS, encoding="utf-8")
        self.assert_refused("git rev-parse HEAD failed")

    def test_invalid_json_in_the_port_corpus_is_refused(self) -> None:
        self.commit_port_corpus("{bad")
        self.assert_refused("is not valid JSON")

    def test_non_list_seeds_in_the_port_corpus_are_refused(self) -> None:
        self.commit_port_corpus('{"ALB": "J50101001A"}')
        self.assert_refused("ALB must be a list of strings")

    def test_unknown_country_in_the_port_corpus_is_refused(self) -> None:
        self.commit_port_corpus('{"XXX": ["1"]}')
        self.assert_refused("XXX")

    def test_new_commit_with_the_same_corpus_is_pinned(self) -> None:
        corpus = (self.copy / "tests" / "parity" / "corpus.json").read_bytes()
        record_path = self.copy / "tests" / "parity" / "expected_python.json"
        old_record = json.loads(record_path.read_text(encoding="utf-8"))
        commit = self.commit_port_corpus(corpus.decode("utf-8"))
        self.assertNotEqual(self.pinned_commit(), commit)

        code, stdout, stderr = self.run_script("--from-port", str(self.port))

        self.assertEqual(0, code, stdout + stderr)
        self.assertEqual(commit, self.pinned_commit())
        self.assertEqual(corpus, (self.copy / "tests" / "parity" / "corpus.json").read_bytes())
        new_record = json.loads(record_path.read_text(encoding="utf-8"))
        self.assertEqual(commit, new_record["corpus"]["commit"])
        old_record["corpus"]["commit"] = commit
        self.assertEqual(old_record, new_record, "only the pinned commit should differ")
        self.assertIn("corpus: copied parity/corpus.json from", stdout)
        self.assertIn(commit, stdout)
        self.assertIn("wrote tests/parity/expected_python.json", stdout)
        self.assertEqual(0, self.run_script("--check")[0], "the regenerated record must be current")

    def test_new_commit_with_a_different_corpus_is_vendored(self) -> None:
        commit = self.commit_port_corpus(self.PORT_CORPUS)

        code, stdout, stderr = self.run_script("--from-port", str(self.port))

        self.assertEqual(0, code, stdout + stderr)
        self.assertEqual(commit, self.pinned_commit())
        self.assertEqual(self.PORT_CORPUS, (self.copy / "tests" / "parity" / "corpus.json").read_text(encoding="utf-8"))
        record = json.loads((self.copy / "tests" / "parity" / "expected_python.json").read_text(encoding="utf-8"))
        self.assertEqual(commit, record["corpus"]["commit"])
        self.assertEqual(["ALB"], sorted(record["valid"]))
        self.assertIn("corpus: copied parity/corpus.json from", stdout)
        self.assertIn("Note these changes on identique/idnumbers-npm", stdout)

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


class RollbackReportTest(TestCase):
    """`main(["--from-port", ...])` reports a failed rollback together with the failure that caused it.

    The script runs in-process against a fake corpus module in a temporary directory, so no tracked file of this
    checkout can be written.
    """

    def setUp(self) -> None:
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.directory = Path(directory.name)
        self.original = {"corpus.json": b"{}\n", "corpus.py": b"# corpus\n", "expected_python.json": b"{}\n"}
        for name, content in self.original.items():
            (self.directory / name).write_bytes(content)
        self.corpus = types.SimpleNamespace(
            CORPUS_PATH=self.directory / "corpus.json",
            EXPECTED_PATH=self.directory / "expected_python.json",
            __file__=str(self.directory / "corpus.py"),
        )
        self.script = load_script()

    def current(self) -> Dict[str, bytes]:
        return {name: (self.directory / name).read_bytes() for name in self.original}

    def half_update_then_raise(self, error: BaseException) -> Callable[[Any, Any], Any]:
        """A stand-in for `copy_from_port` that overwrites the corpus, then fails with `error`."""
        def copy(port: Path, corpus: Any) -> Any:
            corpus.CORPUS_PATH.write_bytes(b"half-updated")
            raise error
        return copy

    def run_main(self, copy: Callable[[Any, Any], Any], restore: Optional[Callable[[Any], None]] = None
                 ) -> Tuple[int, str]:
        """Run `main()` with the fakes in place; return the exit code and standard error."""
        errors = io.StringIO()
        with contextlib.ExitStack() as stack:
            stack.enter_context(mock.patch.object(self.script, "import_corpus_module", lambda: self.corpus))
            stack.enter_context(mock.patch.object(self.script, "copy_from_port", copy))
            if restore is not None:
                stack.enter_context(mock.patch.object(self.script, "restore", restore))
            stack.enter_context(contextlib.redirect_stderr(errors))
            stack.enter_context(contextlib.redirect_stdout(io.StringIO()))
            code = self.script.main(["--from-port", str(self.directory)])
        return code, errors.getvalue()

    def test_failed_rollback_reports_both_failures_and_the_files_to_check(self) -> None:
        calls: List[Dict[Path, Optional[bytes]]] = []

        def failing_restore(snapshot: Dict[Path, Optional[bytes]]) -> None:
            calls.append(snapshot)
            raise PermissionError("restore failure")

        code, stderr = self.run_main(self.half_update_then_raise(RuntimeError("original failure")), failing_restore)

        self.assertEqual(2, code, stderr)
        self.assertEqual(1, len(calls))
        self.assertNotIn("Traceback", stderr)
        self.assertTrue(stderr.startswith("sync_parity_corpus.py: "), stderr)
        self.assertIn("RuntimeError: original failure", stderr)
        self.assertIn("PermissionError: restore failure", stderr)
        self.assertIn("partly updated", stderr)
        for name in self.original:
            self.assertIn(name, stderr)

    def test_failed_rollback_drops_the_cached_bytecode(self) -> None:
        dropped: List[Path] = []

        def failing_restore(snapshot: Dict[Path, Optional[bytes]]) -> None:
            raise PermissionError("restore failure")

        with mock.patch.object(self.script, "drop_bytecode", dropped.append):
            code, stderr = self.run_main(self.half_update_then_raise(RuntimeError("original failure")),
                                         failing_restore)

        self.assertEqual(2, code, stderr)
        self.assertEqual([self.directory / "corpus.py"], dropped)

    def test_successful_rollback_prints_the_original_error_unchanged(self) -> None:
        for error in (self.script.SetupError("cannot read the port"), OSError("disk full")):
            with self.subTest(error=type(error).__name__):
                code, stderr = self.run_main(self.half_update_then_raise(error))
                self.assertEqual(2, code, stderr)
                self.assertEqual("sync_parity_corpus.py: %s\n" % error, stderr)
                self.assertEqual(self.original, self.current())

    def test_successful_rollback_lets_an_unexpected_error_propagate(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "original failure"):
            self.run_main(self.half_update_then_raise(RuntimeError("original failure")))
        self.assertEqual(self.original, self.current())


if __name__ == "__main__":
    main()
