"""Safety and local-Git regression tests for the API documentation rebuild workflow."""

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

from tools import docs_rebuild


ROOT = Path(__file__).resolve().parents[1]
HELPER = ROOT / "tools" / "docs_rebuild.py"


def git(repository, *arguments):
    result = subprocess.run(
        ["git", *arguments],
        cwd=str(repository),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode != 0:
        raise AssertionError(
            "git {} failed: {}".format(" ".join(arguments), result.stderr.decode("utf-8", errors="replace"))
        )
    return result.stdout.decode("utf-8", errors="replace").strip()


class VersionManifestTest(unittest.TestCase):
    def test_strict_parser_rejects_empty_javascript_and_unsafe_versions(self):
        for contents in (
            b"",
            b"window._VERSIONS = [];",
            b"window._VERSIONS = [];\nalert('unsafe');\n",
            b"window._VERSIONS = [];\nwindow._VERSIONS.push('01.2.3');\n",
            b"window._VERSIONS = [];\nwindow._VERSIONS.push('1.2.3');\n\n",
            b"window._VERSIONS = [];\nwindow._VERSIONS.push('1.2.3');\nwindow._VERSIONS.push('1.2.3');",
        ):
            with self.subTest(contents=contents):
                with self.assertRaises(docs_rebuild.DocsRebuildError):
                    docs_rebuild.parse_manifest(contents)

    def test_merge_deduplicates_sorts_numerically_and_is_idempotent(self):
        candidate = docs_rebuild.render_manifest(["1.9.1", "1.10.0", "1.9.1"])
        deployed = docs_rebuild.render_manifest(["1.12.0", "1.9.1", "1.10.0"])
        expected = docs_rebuild.render_manifest(["1.9.1", "1.10.0", "1.12.0"])

        merged = docs_rebuild.merge_manifests(candidate, deployed)

        self.assertEqual(merged, expected)
        self.assertEqual(docs_rebuild.merge_manifests(merged, merged), merged)
        self.assertLess(merged.index(b"'1.9.1'"), merged.index(b"'1.10.0'"))

    def test_bootstrap_adds_first_version_once_and_dev_does_not_enter_history(self):
        first = docs_rebuild.render_manifest(["1.22.0"])
        self.assertEqual(docs_rebuild.merge_manifests(first, None).count(b"'1.22.0'"), 1)

        candidate = docs_rebuild.render_manifest(["1.22.0"])
        deployed = docs_rebuild.render_manifest(["1.23.0"])
        merged = docs_rebuild.merge_manifests(candidate, deployed)
        self.assertNotIn(b"'dev'", merged)
        self.assertEqual(merged.count(b"'1.22.0'"), 1)
        self.assertEqual(merged.count(b"'1.23.0'"), 1)


class SourceInputValidationTest(unittest.TestCase):
    def test_stable_version_and_matching_source_tags_are_strict(self):
        self.assertEqual(docs_rebuild.validate_version(""), "")
        self.assertEqual(docs_rebuild.validate_version("1.22.0"), "1.22.0")
        for value in ("1.02.0", "01.2.3", "1.2", "1.2.3;touch", " 1.2.3", "1.2.3\n"):
            with self.subTest(value=value):
                with self.assertRaises(docs_rebuild.DocsRebuildError):
                    docs_rebuild.validate_version(value)

        self.assertEqual(docs_rebuild.validate_source_ref("v1.22.0", "1.22.0"), "v1.22.0")
        self.assertEqual(
            docs_rebuild.validate_source_ref("refs/tags/v1.22.0", "1.22.0"),
            "v1.22.0",
        )
        for source_ref, version in (
            ("main", "1.22.0"),
            ("refs/heads/main", "1.22.0"),
            ("v1.22.0;echo bad", "1.22.0"),
            ("v1.22.0", "1.23.0"),
            ("v1.22.0", ""),
        ):
            with self.subTest(source_ref=source_ref, version=version):
                with self.assertRaises(docs_rebuild.DocsRebuildError):
                    docs_rebuild.validate_source_ref(source_ref, version)

    def test_selected_source_version_allows_only_one_optional_final_newline(self):
        docs_rebuild.validate_source_version(b"1.22.0", "1.22.0")
        docs_rebuild.validate_source_version(b"1.22.0\n", "1.22.0")
        for contents in (b"1.22.0\n\n", b" 1.22.0", b"1.22.0 ", b"1.22.0\r\n", b"1.23.0\n"):
            with self.subTest(contents=contents):
                with self.assertRaises(docs_rebuild.DocsRebuildError):
                    docs_rebuild.validate_source_version(contents, "1.22.0")


class DocsRebuildGitFixture(unittest.TestCase):
    maxDiff = None

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="idnumbers-docs-rebuild-")
        self.root = Path(self.temporary.name)
        self.remote = self.root / "remote.git"
        self.seed = self.root / "seed"
        self.workspace = self.root / "workspace"
        self.runner_temp = self.root / "runner-temp"
        self.fake_bin = self.root / "bin"
        self.runner_temp.mkdir()
        self.fake_bin.mkdir()

        self._git_init_bare(self.remote)
        git(self.remote, "symbolic-ref", "HEAD", "refs/heads/main")
        self.seed.mkdir()
        git(self.seed, "init")
        git(self.seed, "config", "user.name", "Docs Test")
        git(self.seed, "config", "user.email", "docs-test@example.invalid")
        git(self.seed, "branch", "-M", "main")
        self._write_source("1.22.0", "historical source\n", include_current_helper=False)
        self._commit_seed("Historical v1.22.0 source")
        git(self.seed, "tag", "v1.22.0")
        historical_sha = git(self.seed, "rev-parse", "HEAD")

        self._write_source("1.23.0", "current source\n", include_current_helper=True)
        self._commit_seed("Current main source")
        self.current_sha = git(self.seed, "rev-parse", "HEAD")
        git(self.seed, "remote", "add", "origin", str(self.remote))
        git(self.seed, "push", "origin", "main")
        git(self.seed, "push", "origin", "refs/tags/v1.22.0")

        git(self.seed, "checkout", "--orphan", "gh-pages")
        git(self.seed, "rm", "-rf", ".")
        docs = self.seed / "docs"
        docs.mkdir()
        (docs / "versions.js").write_bytes(docs_rebuild.render_manifest(["1.9.1", "1.10.0", "1.22.0", "1.24.0"]))
        (docs / "index.html").write_text("deployed index\n", encoding="utf-8")
        (docs / "keep.txt").write_text("keep me\n", encoding="utf-8")
        self._commit_seed("Initial gh-pages")
        git(self.seed, "push", "origin", "gh-pages")
        git(self.seed, "checkout", "main")
        git(self.root, "clone", "--branch", "main", str(self.remote), str(self.workspace))
        self.historical_sha = git(self.workspace, "rev-parse", "refs/tags/v1.22.0^{commit}")
        self.assertEqual(self.historical_sha, historical_sha)
        self.pydoctor = self.fake_bin / "pydoctor"
        self._write_fake_pydoctor()

    def tearDown(self):
        self.temporary.cleanup()

    @staticmethod
    def _git_init_bare(path):
        git(path.parent, "init", "--bare", str(path))

    def _write_source(self, version, marker, include_current_helper):
        (self.seed / "VERSION").write_text(version + "\n", encoding="ascii")
        package = self.seed / "idnumbers"
        package.mkdir(exist_ok=True)
        (package / "__init__.py").write_text('"""Test package."""\n', encoding="utf-8")
        (package / "marker.txt").write_text(marker, encoding="utf-8")
        template = self.seed / "docs" / "template"
        template.mkdir(parents=True, exist_ok=True)
        history = ["1.9.1", "1.10.0", "1.22.0"]
        (template / "versions.js").write_bytes(docs_rebuild.render_manifest(history))
        tools = self.seed / "tools"
        tools.mkdir(exist_ok=True)
        helper_path = tools / "docs_rebuild.py"
        if include_current_helper:
            shutil.copyfile(HELPER, helper_path)
        else:
            helper_path.write_text("raise RuntimeError('historical stale helper must not run')\n", encoding="utf-8")

    def _commit_seed(self, message):
        git(self.seed, "add", "--all")
        git(self.seed, "commit", "-m", message)

    def _write_fake_pydoctor(self):
        self.pydoctor.write_text(
            "#!{}\n"
            "from pathlib import Path\n"
            "import sys\n"
            "output = next(arg.split('=', 1)[1] for arg in sys.argv if arg.startswith('--html-output='))\n"
            "destination = Path(output)\n"
            "destination.mkdir(parents=True)\n"
            "marker = Path('idnumbers/marker.txt').read_text(encoding='utf-8')\n"
            "(destination / 'index.html').write_text(marker, encoding='utf-8')\n".format(sys.executable),
            encoding="utf-8",
        )
        self.pydoctor.chmod(0o755)

    def _environment(self, version, source_ref="", caller_sha=None):
        environment = os.environ.copy()
        environment.update(
            {
                "PATH": str(self.fake_bin) + os.pathsep + environment.get("PATH", ""),
                "GITHUB_WORKSPACE": str(self.workspace),
                "RUNNER_TEMP": str(self.runner_temp),
                "IDNUMBERS_DOCS_VERSION": version,
                "IDNUMBERS_DOCS_SOURCE_REF": source_ref,
                "IDNUMBERS_DOCS_CALLER_SHA": caller_sha or self.current_sha,
            }
        )
        return environment

    def prepare_build(self, version, source_ref="", caller_sha=None, workspace=None, runner_temp=None):
        workspace = workspace or self.workspace
        runner_temp = runner_temp or self.runner_temp
        environment = self._environment(version, source_ref, caller_sha)
        environment["GITHUB_WORKSPACE"] = str(workspace)
        environment["RUNNER_TEMP"] = str(runner_temp)
        result = subprocess.run(
            [sys.executable, str(workspace / "tools" / "docs_rebuild.py"), "prepare"],
            cwd=str(workspace),
            env=environment,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        if result.returncode != 0:
            raise AssertionError(result.stderr.decode("utf-8", errors="replace"))
        return result.stdout.decode("utf-8", errors="replace")

    def run_deploy(self, before_push=None, workspace=None, runner_temp=None):
        workspace = workspace or self.workspace
        runner_temp = runner_temp or self.runner_temp
        if before_push is None:
            environment = self._environment("1.22.0", "v1.22.0")
            environment["GITHUB_WORKSPACE"] = str(workspace)
            environment["RUNNER_TEMP"] = str(runner_temp)
            result = subprocess.run(
                [
                    sys.executable,
                    str(runner_temp / docs_rebuild._ORCHESTRATOR_DIR_NAME / docs_rebuild._HELPER_NAME),
                    "deploy",
                ],
                cwd=str(workspace),
                env=environment,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            if result.returncode != 0:
                raise AssertionError(result.stderr.decode("utf-8", errors="replace"))
            return result.stdout.decode("utf-8", errors="replace")
        return docs_rebuild.deploy_workspace(workspace, runner_temp, before_push)

    def _make_remote_advancer(self):
        advancer = self.root / "advancer"
        git(self.root, "clone", "--branch", "gh-pages", str(self.remote), str(advancer))
        git(advancer, "config", "user.name", "Concurrent Docs")
        git(advancer, "config", "user.email", "concurrent@example.invalid")
        return advancer

    def _advance_remote(self, advancer, version, filename, content):
        git(advancer, "pull", "--ff-only", "origin", "gh-pages")
        manifest_path = advancer / "docs" / "versions.js"
        current = docs_rebuild.parse_manifest(manifest_path.read_bytes())
        manifest_path.write_bytes(docs_rebuild.render_manifest(current + [version]))
        target = advancer / "docs" / filename
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        git(advancer, "add", "--", "docs/versions.js", "docs/" + filename)
        git(advancer, "commit", "-m", "Concurrent history {}".format(version))
        git(advancer, "push", "origin", "gh-pages")


class DocsRebuildSourceSelectionTest(DocsRebuildGitFixture):
    def test_default_caller_sha_builds_without_a_tag_and_adds_requested_version_once(self):
        self.assertEqual(git(self.workspace, "tag", "--points-at", self.current_sha), "")
        output = self.prepare_build("1.23.0")

        state = json.loads(
            (self.runner_temp / docs_rebuild._ORCHESTRATOR_DIR_NAME / docs_rebuild._STATE_NAME).read_text()
        )
        self.assertIn(self.current_sha, output)
        self.assertEqual(state["source_sha"], self.current_sha)
        candidate = (self.runner_temp / docs_rebuild._ORCHESTRATOR_DIR_NAME / docs_rebuild._CANDIDATE_NAME).read_bytes()
        self.assertEqual(candidate.count(b"'1.23.0'"), 1)
        self.assertIn(
            b"current source", (self.runner_temp / "idnumbers-docs-build/pydocs/v1.23.0/index.html").read_bytes()
        )
        self.assertEqual(git(self.workspace, "status", "--porcelain"), "")
        self.assertEqual(
            (self.workspace / "docs/template/versions.js").read_bytes(),
            docs_rebuild.render_manifest(["1.9.1", "1.10.0", "1.22.0"]),
        )

    def test_matching_historical_tag_builds_historical_content_with_current_helper(self):
        self.prepare_build("1.22.0", "refs/tags/v1.22.0", self.current_sha)
        output = self.runner_temp / "idnumbers-docs-build/pydocs/v1.22.0/index.html"
        helper_copy = self.runner_temp / "idnumbers-docs-orchestrator/docs_rebuild.py"

        self.assertEqual(output.read_text(encoding="utf-8"), "historical source\n")
        self.assertEqual(helper_copy.read_bytes(), HELPER.read_bytes())
        self.assertNotIn(b"historical stale helper", helper_copy.read_bytes())

    def test_mismatched_default_source_version_fails_before_rendering(self):
        result = subprocess.run(
            [sys.executable, str(self.workspace / "tools" / "docs_rebuild.py"), "prepare"],
            cwd=str(self.workspace),
            env=self._environment("1.22.0", "", self.current_sha),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn(b"does not exactly match", result.stderr)
        self.assertFalse((self.runner_temp / "idnumbers-docs-build").exists())

    def test_empty_version_builds_caller_dev_without_inserting_dev(self):
        self.prepare_build("")

        candidate = (self.runner_temp / "idnumbers-docs-orchestrator/candidate-versions.js").read_bytes()
        current_version = (self.runner_temp / "idnumbers-docs-build/pydocs/dev/current_version.js").read_text(
            encoding="ascii"
        )
        self.assertNotIn(b"'dev'", candidate)
        self.assertIn("= 'dev';", current_version)


class DocsRebuildDeploymentTest(DocsRebuildGitFixture):
    def test_historical_deploy_keeps_newer_versions_and_unrelated_files(self):
        self.prepare_build("1.22.0", "v1.22.0")
        self.run_deploy()

        manifest = (self.workspace / "docs/versions.js").read_bytes()
        self.assertEqual(docs_rebuild.parse_manifest(manifest), ["1.9.1", "1.10.0", "1.22.0", "1.24.0"])
        self.assertEqual((self.workspace / "docs/v1.22.0/index.html").read_text(), "historical source\n")
        self.assertEqual((self.workspace / "docs/keep.txt").read_text(), "keep me\n")
        self.assertEqual((self.workspace / "docs/index.html").read_text(), "deployed index\n")
        self.assertEqual(
            git(self.workspace, "log", "-1", "--format=%an <%ae>"), "Microdata Bot <microdataxyz@outlook.com>"
        )
        self.assertFalse((self.workspace / "tools/docs_rebuild.py").exists())

    def test_repeated_deployment_replaces_only_the_target_and_is_idempotent(self):
        self.prepare_build("1.22.0", "v1.22.0")
        self.run_deploy()
        first_remote_sha = git(self.workspace, "ls-remote", "origin", "refs/heads/gh-pages").split()[0]

        second_workspace = self.root / "second-workspace"
        second_runner_temp = self.root / "second-runner-temp"
        second_runner_temp.mkdir()
        git(self.root, "clone", "--branch", "main", str(self.remote), str(second_workspace))
        self.prepare_build("1.22.0", "v1.22.0", workspace=second_workspace, runner_temp=second_runner_temp)
        self.run_deploy(workspace=second_workspace, runner_temp=second_runner_temp)

        second_remote_sha = git(second_workspace, "ls-remote", "origin", "refs/heads/gh-pages").split()[0]
        self.assertEqual(second_remote_sha, first_remote_sha)
        self.assertEqual((second_workspace / "docs/keep.txt").read_text(), "keep me\n")
        self.assertEqual((second_workspace / "docs/v1.22.0/index.html").read_text(), "historical source\n")

    def test_bootstrap_when_manifest_is_absent_is_explicit_and_preserves_candidate(self):
        advancer = self._make_remote_advancer()
        (advancer / "docs/versions.js").unlink()
        git(advancer, "add", "--", "docs/versions.js")
        git(advancer, "commit", "-m", "Remove absent manifest for bootstrap test")
        git(advancer, "push", "origin", "gh-pages")
        self.prepare_build("1.23.0", "", self.current_sha)

        self.run_deploy()

        deployed = docs_rebuild.parse_manifest((self.workspace / "docs/versions.js").read_bytes())
        self.assertEqual(deployed, ["1.9.1", "1.10.0", "1.22.0", "1.23.0"])

    def test_manifest_read_failure_is_not_mistaken_for_bootstrap(self):
        advancer = self._make_remote_advancer()
        (advancer / "docs/versions.js").write_text("alert('unexpected');\n", encoding="ascii")
        git(advancer, "add", "--", "docs/versions.js")
        git(advancer, "commit", "-m", "Corrupt deployed manifest")
        git(advancer, "push", "origin", "gh-pages")
        self.prepare_build("1.22.0", "v1.22.0")

        with self.assertRaises(docs_rebuild.DocsRebuildError):
            docs_rebuild.deploy_workspace(self.workspace, self.runner_temp)
        self.assertEqual(git(self.workspace, "branch", "--show-current"), "gh-pages")

    def test_initial_fetch_failure_is_not_mistaken_for_bootstrap(self):
        self.prepare_build("1.22.0", "v1.22.0")
        git(self.workspace, "remote", "set-url", "origin", str(self.root / "missing.git"))

        with self.assertRaises(docs_rebuild.GitCommandError):
            docs_rebuild.deploy_workspace(self.workspace, self.runner_temp)

    def test_push_permission_failure_is_not_retried_as_a_stale_branch(self):
        self.prepare_build("1.22.0", "v1.22.0")
        git(self.workspace, "remote", "set-url", "--push", "origin", str(self.root / "missing-push.git"))

        with self.assertRaisesRegex(docs_rebuild.GitCommandError, "without remote advancement"):
            docs_rebuild.deploy_workspace(self.workspace, self.runner_temp)

    def test_rebase_after_concurrent_history_change_preserves_new_entries(self):
        self.prepare_build("1.22.0", "v1.22.0")
        advancer = self._make_remote_advancer()

        def advance(attempt, workspace):
            if attempt == 1:
                self._advance_remote(advancer, "1.25.0", "remote-first.txt", "first remote writer\n")

        docs_rebuild.deploy_workspace(self.workspace, self.runner_temp, advance)

        versions = docs_rebuild.parse_manifest((self.workspace / "docs/versions.js").read_bytes())
        self.assertEqual(versions, ["1.9.1", "1.10.0", "1.22.0", "1.24.0", "1.25.0"])
        self.assertEqual((self.workspace / "docs/remote-first.txt").read_text(), "first remote writer\n")
        self.assertEqual((self.workspace / "docs/keep.txt").read_text(), "keep me\n")

    def test_history_is_refreshed_again_between_retries(self):
        self.prepare_build("1.22.0", "v1.22.0")
        advancer = self._make_remote_advancer()

        def advance(attempt, workspace):
            if attempt == 1:
                self._advance_remote(advancer, "1.25.0", "remote-first.txt", "first remote writer\n")
            elif attempt == 2:
                self._advance_remote(advancer, "1.26.0", "remote-second.txt", "second remote writer\n")

        docs_rebuild.deploy_workspace(self.workspace, self.runner_temp, advance)

        versions = docs_rebuild.parse_manifest((self.workspace / "docs/versions.js").read_bytes())
        self.assertEqual(versions, ["1.9.1", "1.10.0", "1.22.0", "1.24.0", "1.25.0", "1.26.0"])
        self.assertEqual((self.workspace / "docs/remote-first.txt").read_text(), "first remote writer\n")
        self.assertEqual((self.workspace / "docs/remote-second.txt").read_text(), "second remote writer\n")

    def test_rebase_conflict_fails_without_discarding_remote_docs(self):
        self.prepare_build("1.22.0", "v1.22.0")
        advancer = self._make_remote_advancer()
        conflict_file = "v1.22.0/index.html"

        def advance(attempt, workspace):
            if attempt == 1:
                self._advance_remote(advancer, "1.25.0", conflict_file, "remote conflict\n")

        with self.assertRaises(docs_rebuild.GitCommandError):
            docs_rebuild.deploy_workspace(self.workspace, self.runner_temp, advance)

        self.assertNotEqual(git(self.workspace, "status", "--porcelain"), "")
        self.assertIn(
            "remote conflict",
            git(self.workspace, "show", "refs/remotes/origin/gh-pages:docs/v1.22.0/index.html"),
        )

    def test_exhausted_non_force_push_retries_fail(self):
        self.prepare_build("1.22.0", "v1.22.0")
        advancer = self._make_remote_advancer()

        def advance(attempt, workspace):
            self._advance_remote(
                advancer,
                "1.25.{}".format(attempt),
                "race-{}.txt".format(attempt),
                "remote race {}\n".format(attempt),
            )

        with self.assertRaisesRegex(docs_rebuild.GitCommandError, "exhausted 4 attempts"):
            docs_rebuild.deploy_workspace(self.workspace, self.runner_temp, advance)
        self.assertEqual(git(self.workspace, "branch", "--show-current"), "gh-pages")


if __name__ == "__main__":
    unittest.main()
