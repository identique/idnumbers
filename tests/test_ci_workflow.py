"""Contracts for the CI workflow and the repository files that CI and tooling rely on."""

from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
FORMAT_COMMIT = "9ae3d112fb91c38d94f0b2db6abddc68a1a84237"
WORKFLOW = ROOT / ".github/workflows/python-test.yml"
MAIN_PUSH_ONLY = (
    "github.event_name == 'push' && github.ref == 'refs/heads/main' && github.repository == 'identique/idnumbers'"
)


def job_text(name: str) -> str:
    """Return the text of one job of the CI workflow, failing with a readable message if it is missing."""
    text = WORKFLOW.read_text()
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


class CIWorkflowTest(unittest.TestCase):
    def test_lint_job_checks_formatting(self) -> None:
        text = (ROOT / ".github/workflows/python-test.yml").read_text()
        start = text.index("\n  lint:\n")
        end = text.index("\n  coverage:\n", start)
        job = text[start:end]
        self.assertIn("ruff==0.16.10", job)
        self.assertIn("ruff check", job)
        self.assertIn("ruff format --check", job)


class CoverageBadgeWorkflowTest(unittest.TestCase):
    def test_only_the_badge_job_can_write(self) -> None:
        text = WORKFLOW.read_text()
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
        text = WORKFLOW.read_text()
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
