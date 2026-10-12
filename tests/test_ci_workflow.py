"""Contracts for the CI workflow and the repository files that CI and tooling rely on."""

from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
FORMAT_COMMIT = "9ae3d112fb91c38d94f0b2db6abddc68a1a84237"


class CIWorkflowTest(unittest.TestCase):
    def test_lint_job_checks_formatting(self) -> None:
        text = (ROOT / ".github/workflows/python-test.yml").read_text()
        start = text.index("\n  lint:\n")
        end = text.index("\n  coverage:\n", start)
        job = text[start:end]
        self.assertIn("ruff==0.16.10", job)
        self.assertIn("ruff check", job)
        self.assertIn("ruff format --check", job)


class RepositoryFilesTest(unittest.TestCase):
    def test_blame_ignore_revs_lists_full_shas(self) -> None:
        text = (ROOT / ".git-blame-ignore-revs").read_text()
        entries = [line for line in text.splitlines() if line.strip() and not line.startswith("#")]
        self.assertTrue(entries)
        for entry in entries:
            with self.subTest(entry=entry):
                self.assertRegex(entry, r"^[0-9a-f]{40}$")
        self.assertIn(FORMAT_COMMIT, entries)

    def test_markdown_is_not_formatted(self) -> None:
        # ruff would also reformat Python code fences in Markdown, including the generated guides.
        text = (ROOT / "pyproject.toml").read_text()
        self.assertRegex(text, re.compile(r'^\[tool\.ruff\.format\]\n(?:#.*\n)*exclude = \["\*\.md"\]$', re.MULTILINE))
