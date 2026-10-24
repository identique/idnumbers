"""Runtime and deployment contracts for the manual release workflows."""

from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / ".github/workflows"


class ReleaseWorkflowRuntimeTest(unittest.TestCase):
    @staticmethod
    def workflow(name):
        return (WORKFLOWS / name).read_text()

    def test_pinned_runners(self):
        for name, count in (("bump_version.yml", 1), ("docs.yml", 1), ("release_to_pypi.yml", 4)):
            with self.subTest(workflow=name):
                runners = re.findall(r"^    runs-on: (.+)$", self.workflow(name), re.MULTILINE)
                self.assertEqual(runners, ["ubuntu-24.04"] * count)

    def test_supported_action_versions(self):
        expected = {
            "bump_version.yml": ["actions/checkout@v7", "peter-evans/create-pull-request@v8.1.1"],
            "docs.yml": ["actions/checkout@v7", "actions/setup-python@v7"],
            "release_to_pypi.yml": [
                "actions/checkout@v7",
                "actions/setup-python@v7",
                "actions/upload-artifact@v7",
                *(["actions/download-artifact@v8"] * 3),
            ],
        }
        for name, actions in expected.items():
            with self.subTest(workflow=name):
                actual = re.findall(
                    r"^\s+-?\s*uses: ((?:actions/|peter-evans/)[^\s]+)", self.workflow(name), re.MULTILINE
                )
                self.assertEqual(actual, actions)

    def test_bump_bot_contract(self):
        workflow = self.workflow("bump_version.yml")
        for contract in (
            "on:\n  workflow_dispatch:",
            "version:\n        description:",
            "required: true",
            "permissions:\n  contents: write\n  pull-requests: write",
            'echo "${{ inputs.version }}" > VERSION',
            "echo \"window._VERSIONS.push('${{ inputs.version }}');\" >> docs/template/versions.js",
            "id: cpr",
            "token: ${{ secrets.GITHUB_TOKEN }}",
            "commit-message: Bump version to ${{ inputs.version }}",
            "committer: Microdata Bot <microdataxyz@outlook.com>",
            "title: Bump version to ${{ inputs.version }}",
            "body: Bump version by ${{ github.actor }}",
            "if: ${{ steps.cpr.outputs.pull-request-number }}",
            "steps.cpr.outputs.pull-request-url",
        ):
            with self.subTest(contract=contract):
                self.assertIn(contract, workflow)
        self.assertNotIn("id-token:", workflow)
        self.assertEqual(re.findall(r"secrets\.([A-Z_]+)", workflow), ["GITHUB_TOKEN"])

    def test_docs_deployment_contract(self):
        workflow = self.workflow("docs.yml")
        for contract in (
            "workflow_dispatch:",
            "workflow_call:",
            "type: string",
            "permissions:\n  contents: write\n  pages: write",
            "fetch-depth: 0",
            "python-version: '3.10'",
            "pip install pydoctor==22.9.1",
            "git checkout origin/gh-pages -b gh-pages",
            'git config --local user.email "microdataxyz@outlook.com"',
            'git config --local user.name "Microdata Bot"',
            "cp docs/template/versions.js pydocs/",
            "cp pydocs/versions.js ./docs/versions.js",
            "--html-output=pydocs/dev",
            "--html-output=pydocs/v${{ inputs.version }}",
            "cp -rf pydocs/* ./docs",
            "rm -rf ./docs/v${{ inputs.version }}",
            "cp -rf pydocs/v${{ inputs.version }} ./docs/v${{ inputs.version }}",
            'git diff-index --quiet HEAD || git commit -m "Update dev doc"',
            'git diff-index --quiet HEAD || git commit -m "Add release doc v${{ inputs.version }}"',
            "git push origin gh-pages",
        ):
            with self.subTest(contract=contract):
                self.assertIn(contract, workflow)
        self.assertEqual(workflow.count("--docformat=restructuredtext"), 2)
        self.assertEqual(workflow.count("if: inputs.version == ''"), 2)
        self.assertEqual(workflow.count("if: inputs.version != ''"), 2)
        self.assertNotIn("persist-credentials: false", workflow)
        self.assertNotIn("id-token:", workflow)

    def test_docs_deploys_queue_per_group_and_retry_a_rejected_push(self):
        workflow = self.workflow("docs.yml")
        group = "concurrency:\n      group: apidoc-${{ inputs.version || 'dev' }}\n      cancel-in-progress: false\n"
        self.assertEqual(workflow.count(group), 1)
        self.assertNotIn("cancel-in-progress: true", workflow)
        push = workflow.split("      - name: push gh-pages\n", 1)[1]
        for contract in (
            "for attempt in 1 2 3; do",
            "git push origin gh-pages && exit 0",
            "git pull --rebase origin gh-pages",
            "done\n          exit 1",
        ):
            with self.subTest(contract=contract):
                self.assertIn(contract, push)
        self.assertEqual(workflow.count("git push"), 1)
        self.assertNotRegex(workflow, r"git push\b[^\n]*(--force|\s-f\b)")

    def test_release_token_route_stays_default(self):
        workflow = self.workflow("release_to_pypi.yml")
        inputs = workflow.split("permissions:", 1)[0]
        self.assertIn("workflow_dispatch:", inputs)
        self.assertNotIn("workflow_call:", inputs)
        self.assertIn("trusted-publishing:\n        type: boolean\n        default: false", inputs)
        self.assertIn('python-version: "3.12"', workflow)
        self.assertIn('version: "0.12.1"', workflow)
        token = workflow.split("  publish-token:", 1)[1].split("  publish-trusted:", 1)[0]
        self.assertIn("if: needs.build.outputs.target == 'pypi' && !inputs.trusted-publishing", token)
        self.assertIn("password: ${{ secrets.PYPI_API_TOKEN }}", token)
        self.assertIn("attestations: false", token)
        self.assertNotIn("id-token:", token)
        self.assertNotIn("skip-existing:", workflow)
