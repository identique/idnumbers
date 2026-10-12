"""Contracts for the CI workflow and the repository files that CI and tooling rely on."""

from pathlib import Path
import re
import unittest
from typing import Optional

ROOT = Path(__file__).resolve().parents[1]
FORMAT_COMMIT = "9ae3d112fb91c38d94f0b2db6abddc68a1a84237"
WORKFLOW = ROOT / ".github/workflows/python-test.yml"
MAIN_PUSH_ONLY = (
    "github.event_name == 'push' && github.ref == 'refs/heads/main' && github.repository == 'identique/idnumbers'"
)


def job_text(name: str, text: Optional[str] = None) -> str:
    """Return the text of one job of the CI workflow, failing with a readable message if it is missing."""
    if text is None:
        text = WORKFLOW.read_text(encoding="utf-8")
    headers = list(re.finditer(r"^  ([A-Za-z][\w-]*):[ \t]*$", text, re.MULTILINE))
    names = [header.group(1) for header in headers]
    if name not in names:
        raise AssertionError(f"job {name!r} is not in {WORKFLOW.name}; its jobs are {names}")
    index = names.index(name)
    end = headers[index + 1].start() if index + 1 < len(headers) else len(text)
    return text[headers[index].start() : end]


def job_needs(name: str) -> "list[str]":
    """Return the ``needs:`` entries of a job (empty when it has none)."""
    match = re.search(r"^    needs:[ \t]*(.+)$", job_text(name), re.MULTILINE)
    if match is None:
        return []
    return [entry.strip() for entry in match.group(1).strip("[]").split(",") if entry.strip()]


def steps(job: str) -> "list[str]":
    """Split a job's text into its steps (each starting at ``- name:`` or ``- uses:``)."""
    return re.split(r"(?m)^(?=    - (?:name|uses):)", job)[1:]


def markdown_format_excluded(text: str) -> bool:
    """Check the formatter's exclude array, ignoring comments and unrelated TOML sections/keys."""
    # Keep quoted strings intact so a '#' within an exclusion is not mistaken for a comment.
    quoted = r'"(?:\\.|[^"\\])*"|\'[^\']*\''
    text = re.sub(quoted + r"|#[^\n]*", lambda match: "" if match.group().startswith("#") else match.group(), text)
    section = re.search(r"(?ms)^\[tool\.ruff\.format\][ \t]*\n(.*?)(?=^[ \t]*\[[A-Za-z]|\Z)", text)
    if section is None:
        return False
    exclude = re.search(r"(?m)^[ \t]*exclude[ \t]*=[ \t]*\[((?:" + quoted + r"|[^\]\"'])*?)\]", section.group(1))
    if exclude is None:
        return False
    return any(match.group() in ('"*.md"', "'*.md'") for match in re.finditer(quoted, exclude.group(1)))


class CIWorkflowTest(unittest.TestCase):
    def assert_lint_checks(self, text: Optional[str] = None) -> None:
        job = job_text("lint", text)
        self.assertIn("ruff==0.16.10", job)
        self.assertIn("ruff check", job)
        self.assertIn("ruff format --check", job)

    def test_lint_job_checks_formatting(self) -> None:
        self.assert_lint_checks()

    def test_lint_contract_tolerates_reordered_jobs_and_missing_coverage(self) -> None:
        lint = "  lint:\n    run: ruff==0.16.10 && ruff check . && ruff format --check .\n"
        other = "  other:\n    run: echo other\n"
        coverage = "  coverage:\n    run: echo coverage\n"
        for text in (coverage + lint + other, other + lint, lint + other + coverage):
            with self.subTest(text=text):
                self.assertEqual(job_text("lint", text), lint)
                self.assert_lint_checks(text)

    def test_missing_or_renamed_lint_job_has_readable_failure(self) -> None:
        for text in ("jobs:\n", "  renamed-lint:\n    run: ruff check .\n"):
            with self.subTest(text=text):
                with self.assertRaisesRegex(AssertionError, "job 'lint' is not in python-test.yml; its jobs are"):
                    self.assert_lint_checks(text)

    def test_formatting_check_in_another_job_does_not_satisfy_lint_contract(self) -> None:
        text = "  lint:\n    run: ruff==0.16.10 && ruff check .\n  other:\n    run: ruff format --check .\n"
        with self.assertRaisesRegex(AssertionError, "ruff format --check"):
            self.assert_lint_checks(text)


class CoverageBadgeWorkflowTest(unittest.TestCase):
    def test_only_the_badge_job_can_write(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertRegex(text, r"(?m)^permissions:\n  contents: read\n")
        self.assertEqual(text.count("contents: write"), 1)
        self.assertEqual(text.count("permissions:"), 2)
        self.assertIn("contents: write", job_text("coverage-badge"))

    def test_badge_job_runs_only_for_pushes_to_main_of_this_repository(self) -> None:
        job = job_text("coverage-badge")
        self.assertRegex(job, r"(?m)^    if: " + re.escape(MAIN_PUSH_ONLY) + r"$")
        self.assertEqual(job_needs("coverage-badge"), ["coverage"])

    def test_badge_job_is_not_a_ci_summary_need(self) -> None:
        # ci-summary fails on a skipped need, and the badge job is skipped on pull requests.
        needs = job_needs("ci-summary")
        self.assertTrue(needs)
        self.assertNotIn("coverage-badge", needs)
        self.assertIn("coverage", needs)

    def test_badge_job_serializes_runs_without_cancelling(self) -> None:
        job = job_text("coverage-badge")
        self.assertRegex(job, r"concurrency:\n      group: coverage-badge\n      cancel-in-progress: false\n")

    def test_the_only_secret_is_the_github_token_and_it_stays_out_of_urls(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertEqual(set(re.findall(r"secrets\.(\w+)", text)), {"GITHUB_TOKEN"})
        self.assertEqual(len(re.findall(r"\$\{\{\s*secrets\.", job_text("coverage-badge"))), 1)
        self.assertNotRegex(text, r"x-access-token:[^\s'\"]*@")
        self.assertNotRegex(text, r"https?://[^\s'\"]*(?:x-access-token|GITHUB_TOKEN|\$\{?encoded)")
        script = job_text("coverage-badge")
        self.assertIn("-c http.extraheader=", script)
        self.assertIn("::add-mask::", script)

    def test_orphan_branch_starts_only_when_ls_remote_reports_a_missing_branch(self) -> None:
        job = job_text("coverage-badge")
        probe = job.index("ls-remote --exit-code --heads")
        missing = job.index('elif [ "$probe" -eq 2 ]; then')
        orphan = job.index("checkout --quiet --orphan badges")
        failure = job.index("else\n", missing)
        self.assertEqual(job.count("--orphan"), 1)
        self.assertLess(probe, missing)
        self.assertLess(missing, orphan)
        self.assertLess(orphan, failure)
        self.assertIn('exit "$probe"', job[failure:])
        self.assertIn("not touching the badges branch", job[failure:])
        self.assertIn('if [ "$probe" -eq 0 ]; then', job[probe:missing])

    def test_coverage_job_builds_the_badge_only_for_pushes_to_main(self) -> None:
        job = job_text("coverage")
        guarded = [step for step in steps(job) if re.search(r"coverage json|coverage_badge|upload-artifact", step)]
        self.assertEqual(len(guarded), 2)
        for step in guarded:
            with self.subTest(step=step.splitlines()[0]):
                self.assertRegex(step, r"(?m)^      if: " + re.escape(MAIN_PUSH_ONLY) + r"$")
        # The floor and the job summary are kept, on every run.
        report = [step for step in steps(job) if "coverage report" in step]
        self.assertEqual(len(report), 1)
        self.assertNotIn("if:", report[0])
        self.assertIn("coverage report --format=markdown", report[0])
        self.assertIn('tee -a "$GITHUB_STEP_SUMMARY"', report[0])

    def test_badge_artifact_is_handed_from_the_coverage_job_to_the_badge_job(self) -> None:
        upload = job_text("coverage")
        download = job_text("coverage-badge")
        self.assertIn("name: coverage-badge", upload)
        self.assertIn("path: coverage-badge/coverage.json", upload)
        self.assertIn("if-no-files-found: error", upload)
        self.assertIn("actions/download-artifact@v8", download)
        self.assertIn("name: coverage-badge", download)

    def test_typecheck_job_covers_the_badge_tool(self) -> None:
        job = job_text("typecheck").replace("\\\n", " ")
        self.assertRegex(job, r"mypy --strict [^\n]*tools/coverage_badge\.py")


class RepositoryFilesTest(unittest.TestCase):
    def test_blame_ignore_revs_lists_full_shas(self) -> None:
        text = (ROOT / ".git-blame-ignore-revs").read_text(encoding="utf-8")
        entries = [line for line in text.splitlines() if line.strip() and not line.startswith("#")]
        self.assertTrue(entries)
        for entry in entries:
            with self.subTest(entry=entry):
                self.assertRegex(entry, r"^[0-9a-f]{40}$")
        self.assertIn(FORMAT_COMMIT, entries)

    def test_markdown_is_not_formatted(self) -> None:
        # ruff would also reformat Python code fences in Markdown, including the generated guides.
        text = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
        self.assertTrue(markdown_format_excluded(text), "tool.ruff.format.exclude must include *.md")

    def test_markdown_exclusion_tolerates_extra_keys_entries_and_whitespace(self) -> None:
        for text in (
            '[tool.ruff.format]\nquote-style = "single"\nexclude = ["build/*", "*.md"]\n',
            "[tool.ruff.format]\nexclude = [\n  'build/*', # extra exclusion\n  '*.md',\n]\npreview = true\n",
            '[tool.ruff.format]  \n  exclude  =  ["*.md", "has#hash.py"] # comment\n[tool.ruff.lint]\n',
        ):
            with self.subTest(text=text):
                self.assertTrue(markdown_format_excluded(text))

    def test_markdown_exclusion_requires_actual_formatter_array_entry(self) -> None:
        for text in (
            '[tool.ruff.format]\nexclude = ["*.rst"]\n',
            '[tool.ruff.lint]\nexclude = ["*.md"]\n',
            '[tool.ruff.format]\npreview = true\n[tool.ruff.lint]\nexclude = ["*.md"]\n',
            '[tool.ruff.format]\n# exclude = ["*.md"]\nexclude = ["*.py"]\n',
            '[tool.ruff.format]\nexclude = ["*.py", # "*.md"\n]\n',
            '[tool.ruff.format]\nother = "*.md"\nexclude = ["*.py"]\n',
            '[tool.ruff.format]\nexclude = "*.md"\n',
            '[tool.ruff.format]\nexclude = ["prefix*.md"]\n',
        ):
            with self.subTest(text=text):
                self.assertFalse(markdown_format_excluded(text))
