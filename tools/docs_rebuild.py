#!/usr/bin/env python3
"""Build versioned API documentation and deploy it without losing gh-pages history."""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import sys
import tarfile
from typing import Callable, Dict, List, Optional, Sequence, Tuple


_VERSION_RE = re.compile(r"(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\Z")
_CALLER_SHA_RE = re.compile(r"[0-9a-fA-F]{40}\Z")
_INIT_LINE = b"window._VERSIONS = [];\n"
_PUSH_RE = re.compile(rb"window\._VERSIONS\.push\('((?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*))'\);\n")
_BUILD_DIR_NAME = "idnumbers-docs-build"
_ORCHESTRATOR_DIR_NAME = "idnumbers-docs-orchestrator"
_STATE_NAME = "state.json"
_CANDIDATE_NAME = "candidate-versions.js"
_HELPER_NAME = "docs_rebuild.py"
_MAX_REBASE_ATTEMPTS = 3


class DocsRebuildError(RuntimeError):
    """Raised when the documentation build or deployment cannot be completed safely."""


class GitCommandError(DocsRebuildError):
    """Raised when a git command fails."""


def _version_tuple(version: str) -> Tuple[int, int, int]:
    if _VERSION_RE.fullmatch(version) is None:
        raise DocsRebuildError("Expected a stable numeric X.Y.Z version")
    parts = [int(part) for part in version.split(".")]
    return parts[0], parts[1], parts[2]


def validate_version(value: str) -> str:
    """Validate a workflow version input; the empty string means a development build."""
    if value == "":
        return ""
    _version_tuple(value)
    return value


def validate_source_ref(source_ref: str, version: str) -> Optional[str]:
    """Return the matching tag name, or None when the caller SHA is the source."""
    if source_ref == "":
        return None
    if version == "":
        raise DocsRebuildError("source-ref is only supported for a versioned documentation build")
    tag = source_ref
    if tag.startswith("refs/tags/"):
        tag = tag[len("refs/tags/") :]
    if not tag.startswith("v") or _VERSION_RE.fullmatch(tag[1:]) is None:
        raise DocsRebuildError("source-ref must be vX.Y.Z or refs/tags/vX.Y.Z")
    if tag[1:] != version:
        raise DocsRebuildError("source-ref tag version must match the requested version")
    return tag


def validate_source_version(contents: bytes, expected_version: str) -> None:
    """Require VERSION to be exactly the selected stable version, optionally newline-terminated."""
    if not expected_version:
        raise DocsRebuildError("A stable version is required when checking source VERSION")
    expected = expected_version.encode("ascii")
    if contents not in (expected, expected + b"\n"):
        raise DocsRebuildError("Selected source VERSION does not exactly match the requested version")


def parse_manifest(contents: bytes) -> List[str]:
    """Parse only the repository's canonical versions.js initialization-and-push grammar."""
    if not contents:
        raise DocsRebuildError("Version manifest is empty")
    try:
        contents.decode("ascii")
    except UnicodeDecodeError as error:
        raise DocsRebuildError("Version manifest must contain ASCII only") from error
    lines = contents.splitlines(keepends=True)
    if not lines or lines[0] != _INIT_LINE:
        raise DocsRebuildError("Version manifest has an unexpected initialization line")
    versions: List[str] = []
    for line in lines[1:]:
        match = _PUSH_RE.fullmatch(line)
        if match is None:
            raise DocsRebuildError("Version manifest contains an unexpected or unsafe line")
        versions.append(match.group(1).decode("ascii"))
    return versions


def render_manifest(versions: Sequence[str]) -> bytes:
    """Render stable versions in deterministic numeric order, removing duplicates."""
    unique = set()
    for version in versions:
        _version_tuple(version)
        unique.add(version)
    ordered = sorted(unique, key=_version_tuple)
    return _INIT_LINE + b"".join(
        ("window._VERSIONS.push('{}');\n".format(version)).encode("ascii") for version in ordered
    )


def merge_manifests(candidate: bytes, deployed: Optional[bytes]) -> bytes:
    """Merge a current candidate with deployed history; None means an absent bootstrap manifest."""
    versions = parse_manifest(candidate)
    if deployed is not None:
        versions.extend(parse_manifest(deployed))
    return render_manifest(versions)


def _diagnostic(result: subprocess.CompletedProcess[bytes]) -> str:
    detail = result.stderr.decode("utf-8", errors="replace").strip()
    return detail or "no diagnostic output"


def _run_git(workspace: Path, *arguments: str, check: bool = True) -> subprocess.CompletedProcess[bytes]:
    try:
        result = subprocess.run(
            ["git", *arguments],
            cwd=str(workspace),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
    except OSError as error:
        raise GitCommandError("Could not run git {}: {}".format(" ".join(arguments), error)) from error
    if check and result.returncode != 0:
        raise GitCommandError(
            "git {} failed with exit {}: {}".format(" ".join(arguments), result.returncode, _diagnostic(result))
        )
    return result


def _git_text(workspace: Path, *arguments: str) -> str:
    return _run_git(workspace, *arguments).stdout.decode("ascii").strip()


def _git_root(workspace: Path) -> Path:
    root = Path(_git_text(workspace, "rev-parse", "--show-toplevel")).resolve()
    if root != workspace.resolve():
        raise DocsRebuildError("GITHUB_WORKSPACE must be the repository root")
    return root


def resolve_source(workspace: Path, version: str, source_ref: str, caller_sha: str) -> str:
    """Resolve either a matching version tag or the exact caller commit."""
    version = validate_version(version)
    tag = validate_source_ref(source_ref, version)
    if tag is not None:
        revision = "refs/tags/{}^{{commit}}".format(tag)
        commit = _git_text(workspace, "rev-parse", "--verify", revision)
    else:
        if _CALLER_SHA_RE.fullmatch(caller_sha) is None:
            raise DocsRebuildError("github.sha must be a 40-character hexadecimal commit SHA")
        revision = "{}^{{commit}}".format(caller_sha)
        commit = _git_text(workspace, "rev-parse", "--verify", revision)
    if _CALLER_SHA_RE.fullmatch(commit) is None:
        raise DocsRebuildError("Resolved documentation source is not a 40-character commit SHA")
    if version:
        source_version = _run_git(workspace, "show", "{}:VERSION".format(commit)).stdout
        validate_source_version(source_version, version)
    print("Resolved docs source commit: {}".format(commit), flush=True)
    return commit


def _safe_extract_source(workspace: Path, commit: str, destination: Path) -> None:
    """Extract only the package and pydoctor template from an exact git archive."""
    archive = _run_git(workspace, "archive", "--format=tar", commit).stdout
    destination.mkdir(parents=True, exist_ok=False)
    wanted_roots = {"idnumbers", "docs/template"}
    extracted: set[str] = set()
    try:
        with tarfile.open(fileobj=io.BytesIO(archive), mode="r:") as bundle:
            for member in bundle:
                name = PurePosixPath(member.name)
                if name.is_absolute() or not name.parts or any(part in (".", "..") for part in name.parts):
                    raise DocsRebuildError("Selected source archive contains an unsafe path")
                relative = name.as_posix()
                if not any(relative == root or relative.startswith(root + "/") for root in wanted_roots):
                    continue
                if not (member.isdir() or member.isfile()):
                    raise DocsRebuildError("Selected source package/templates contain a non-regular file")
                target = destination.joinpath(*name.parts)
                target.parent.mkdir(parents=True, exist_ok=True)
                if member.isdir():
                    target.mkdir(exist_ok=True)
                    continue
                if relative in extracted:
                    raise DocsRebuildError("Selected source archive contains a duplicate file")
                extracted.add(relative)
                stream = bundle.extractfile(member)
                if stream is None:
                    raise DocsRebuildError("Could not read selected source archive file")
                with stream, target.open("xb") as output:
                    shutil.copyfileobj(stream, output)
    except (tarfile.TarError, OSError) as error:
        if isinstance(error, DocsRebuildError):
            raise
        raise DocsRebuildError("Could not safely extract selected source: {}".format(error)) from error
    if not (destination / "idnumbers").is_dir() or not (destination / "docs" / "template").is_dir():
        raise DocsRebuildError("Selected source is missing idnumbers/ or docs/template/")


def _write_file(path: Path, contents: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_bytes(contents)
    temporary.replace(path)


def prepare(
    workspace: Path,
    runner_temp: Path,
    version: str,
    source_ref: str,
    caller_sha: str,
) -> Dict[str, str]:
    """Validate inputs, build from the selected commit and stage the current deploy helper."""
    workspace = workspace.resolve()
    runner_temp = runner_temp.resolve()
    _git_root(workspace)
    version = validate_version(version)
    commit = resolve_source(workspace, version, source_ref, caller_sha)

    template_path = workspace / "docs" / "template" / "versions.js"
    if template_path.is_symlink() or not template_path.is_file():
        raise DocsRebuildError("Current orchestration docs/template/versions.js is missing or not a regular file")
    base_manifest = template_path.read_bytes()
    base_versions = parse_manifest(base_manifest)
    candidate = render_manifest(base_versions + ([version] if version else []))

    build_root = runner_temp / _BUILD_DIR_NAME
    orchestrator_root = runner_temp / _ORCHESTRATOR_DIR_NAME
    for path in (build_root, orchestrator_root):
        if path.is_symlink():
            raise DocsRebuildError("Runner temporary output path must not be a symlink")
        if path.exists():
            shutil.rmtree(path)
    build_root.mkdir(parents=True)
    orchestrator_root.mkdir(parents=True)

    source_root = build_root / "source"
    _safe_extract_source(workspace, commit, source_root)
    target_name = "v{}".format(version) if version else "dev"
    target_output = build_root / "pydocs" / target_name
    target_output.parent.mkdir(parents=True)
    project_version = version or "dev"
    command = [
        "pydoctor",
        "--docformat=restructuredtext",
        "--make-html",
        "--html-output={}".format(target_output.resolve()),
        "--project-name=idnumbers",
        "--project-version={}".format(project_version),
        "--project-url=https://github.com/identique/idnumbers",
        "--template-dir={}".format((source_root / "docs" / "template").resolve()),
        "idnumbers",
    ]
    environment = os.environ.copy()
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    try:
        result = subprocess.run(
            command,
            cwd=str(source_root),
            env=environment,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
    except OSError as error:
        raise DocsRebuildError("Could not run pinned pydoctor: {}".format(error)) from error
    if result.returncode != 0:
        output = result.stdout.decode("utf-8", errors="replace").strip()
        raise DocsRebuildError("pydoctor failed with exit {}: {}".format(result.returncode, output))
    if not target_output.is_dir():
        raise DocsRebuildError("pydoctor did not create the expected documentation output directory")
    current_version = version or "dev"
    (target_output / "current_version.js").write_text(
        "window._CURRENT_VERSION = '{}';\n".format(current_version), encoding="ascii"
    )

    helper_source = workspace / "tools" / _HELPER_NAME
    if helper_source.is_symlink() or not helper_source.is_file():
        raise DocsRebuildError("Current orchestration helper is missing or not a regular file")
    shutil.copyfile(str(helper_source), str(orchestrator_root / _HELPER_NAME))
    _write_file(orchestrator_root / _CANDIDATE_NAME, candidate)
    state = {
        "version": version,
        "source_sha": commit,
        "target_name": target_name,
        "manifest_sha256": hashlib.sha256(candidate).hexdigest(),
    }
    _write_file(
        orchestrator_root / _STATE_NAME,
        (json.dumps(state, sort_keys=True, separators=(",", ":")) + "\n").encode("ascii"),
    )
    print("Built API documentation for {} from {}".format(project_version, commit), flush=True)
    return state


def _load_prepared(runner_temp: Path) -> Tuple[Dict[str, str], bytes, Path]:
    build_root = runner_temp / _BUILD_DIR_NAME
    orchestrator_root = runner_temp / _ORCHESTRATOR_DIR_NAME
    try:
        state = json.loads((orchestrator_root / _STATE_NAME).read_text(encoding="ascii"))
        candidate = (orchestrator_root / _CANDIDATE_NAME).read_bytes()
    except (OSError, UnicodeError, ValueError) as error:
        raise DocsRebuildError("Prepared documentation state is missing or invalid") from error
    if not isinstance(state, dict) or set(state) != {"version", "source_sha", "target_name", "manifest_sha256"}:
        raise DocsRebuildError("Prepared documentation state has an unexpected shape")
    version_value = state.get("version")
    source_sha = state.get("source_sha")
    target_name = state.get("target_name")
    manifest_sha = state.get("manifest_sha256")
    if not isinstance(version_value, str) or not isinstance(source_sha, str):
        raise DocsRebuildError("Prepared documentation state has invalid values")
    if not isinstance(target_name, str) or not isinstance(manifest_sha, str):
        raise DocsRebuildError("Prepared documentation state has invalid paths or digest")
    version = validate_version(version_value)
    if _CALLER_SHA_RE.fullmatch(source_sha) is None:
        raise DocsRebuildError("Prepared documentation source SHA is invalid")
    expected_target = "v{}".format(version) if version else "dev"
    if target_name != expected_target:
        raise DocsRebuildError("Prepared documentation target path is invalid")
    if hashlib.sha256(candidate).hexdigest() != manifest_sha:
        raise DocsRebuildError("Prepared version manifest changed after the build")
    parse_manifest(candidate)
    output = build_root / "pydocs" / expected_target
    if output.is_symlink() or not output.is_dir():
        raise DocsRebuildError("Prepared documentation output is missing or unsafe")
    return state, candidate, output


def _fetch_gh_pages(workspace: Path) -> str:
    _run_git(
        workspace,
        "fetch",
        "--no-tags",
        "origin",
        "refs/heads/gh-pages:refs/remotes/origin/gh-pages",
    )
    return _git_text(workspace, "rev-parse", "--verify", "refs/remotes/origin/gh-pages^{commit}")


def _read_manifest_at_ref(workspace: Path, ref: str) -> Optional[bytes]:
    entries = _run_git(workspace, "ls-tree", "-z", ref, "--", "docs/versions.js").stdout
    if not entries:
        return None
    records = entries.split(b"\0")
    if len(records) != 2 or not records[0]:
        raise DocsRebuildError("Deployed version manifest path is malformed")
    try:
        metadata, path = records[0].split(b"\t", 1)
        mode, object_type, object_sha = metadata.split(b" ")
    except ValueError as error:
        raise DocsRebuildError("Deployed version manifest tree entry is malformed") from error
    if path != b"docs/versions.js" or object_type != b"blob" or mode not in (b"100644", b"100755"):
        raise DocsRebuildError("Deployed version manifest is not a regular file")
    return _run_git(workspace, "cat-file", "blob", object_sha.decode("ascii")).stdout


def _write_worktree_manifest(workspace: Path, contents: bytes) -> None:
    docs_dir = workspace / "docs"
    if docs_dir.is_symlink() or (docs_dir.exists() and not docs_dir.is_dir()):
        raise DocsRebuildError("Deployed docs directory is not a regular directory")
    docs_dir.mkdir(exist_ok=True)
    path = docs_dir / "versions.js"
    if path.is_symlink() or (path.exists() and not path.is_file()):
        raise DocsRebuildError("Deployed version manifest is not a regular file")
    if not path.exists() or path.read_bytes() != contents:
        _write_file(path, contents)


def _replace_output(source: Path, workspace: Path, target_name: str) -> None:
    docs_dir = workspace / "docs"
    if docs_dir.is_symlink() or (docs_dir.exists() and not docs_dir.is_dir()):
        raise DocsRebuildError("Deployed docs directory is not a regular directory")
    docs_dir.mkdir(exist_ok=True)
    target = docs_dir / target_name
    if target.is_symlink() or target.is_file():
        target.unlink()
    elif target.exists():
        if not target.is_dir():
            raise DocsRebuildError("Documentation target is not a regular directory")
        shutil.rmtree(target)
    shutil.copytree(source, target)


def _commit_staged(workspace: Path, message: str) -> None:
    status = _run_git(workspace, "diff", "--cached", "--quiet", check=False)
    if status.returncode == 0:
        return
    if status.returncode != 1:
        raise GitCommandError("git diff --cached --quiet failed: {}".format(_diagnostic(status)))
    _run_git(workspace, "commit", "-m", message)


def _stage_initial_deployment(workspace: Path, output: Path, candidate: bytes, version: str, target_name: str) -> None:
    deployed = _read_manifest_at_ref(workspace, "refs/remotes/origin/gh-pages")
    merged = merge_manifests(candidate, deployed)
    _replace_output(output, workspace, target_name)
    _write_worktree_manifest(workspace, merged)
    target_path = "docs/{}".format(target_name)
    _run_git(workspace, "add", "--", target_path, "docs/versions.js")
    message = "Update dev doc" if not version else "Add release doc v{}".format(version)
    _commit_staged(workspace, message)


def _is_ancestor(workspace: Path, commit: str, head: str) -> bool:
    result = _run_git(workspace, "merge-base", "--is-ancestor", commit, head, check=False)
    if result.returncode == 0:
        return True
    if result.returncode == 1:
        return False
    raise GitCommandError("git merge-base --is-ancestor failed: {}".format(_diagnostic(result)))


BeforePush = Callable[[int, Path], None]


def deploy_workspace(workspace: Path, runner_temp: Path, before_push: Optional[BeforePush] = None) -> None:
    """Deploy a prepared build, refreshing and merging remote history after each successful rebase."""
    workspace = workspace.resolve()
    runner_temp = runner_temp.resolve()
    _git_root(workspace)
    state, candidate, output = _load_prepared(runner_temp)
    version = state["version"]
    target_name = state["target_name"]
    print("Deploying API docs built from {}".format(state["source_sha"]), flush=True)
    _run_git(workspace, "config", "--local", "user.email", "microdataxyz@outlook.com")
    _run_git(workspace, "config", "--local", "user.name", "Microdata Bot")

    _fetch_gh_pages(workspace)
    _run_git(workspace, "checkout", "-B", "gh-pages", "refs/remotes/origin/gh-pages")
    _stage_initial_deployment(workspace, output, candidate, version, target_name)

    total_push_attempts = _MAX_REBASE_ATTEMPTS + 1
    for attempt in range(1, total_push_attempts + 1):
        remote_before = _git_text(workspace, "rev-parse", "--verify", "refs/remotes/origin/gh-pages^{commit}")
        if before_push is not None:
            before_push(attempt, workspace)
        push = _run_git(workspace, "push", "origin", "gh-pages:gh-pages", check=False)
        if push.returncode == 0:
            print("Pushed gh-pages on attempt {}".format(attempt), flush=True)
            return

        if attempt > _MAX_REBASE_ATTEMPTS:
            raise GitCommandError(
                "gh-pages push exhausted {} attempts: {}".format(total_push_attempts, _diagnostic(push))
            )

        remote_after = _fetch_gh_pages(workspace)
        if remote_after == remote_before:
            raise GitCommandError(
                "gh-pages push failed without remote advancement (check authentication/permissions): {}".format(
                    _diagnostic(push)
                )
            )
        _run_git(workspace, "pull", "--rebase", "origin", "gh-pages")

        # Refresh once more after rebase so the merge includes the newest fetched history before retrying.
        latest_remote = _fetch_gh_pages(workspace)
        if not _is_ancestor(workspace, latest_remote, _git_text(workspace, "rev-parse", "HEAD")):
            _run_git(workspace, "pull", "--rebase", "origin", "gh-pages")
            latest_remote = _fetch_gh_pages(workspace)
            if not _is_ancestor(workspace, latest_remote, _git_text(workspace, "rev-parse", "HEAD")):
                raise DocsRebuildError("gh-pages kept advancing during rebase; refusing a stale-history retry")
        latest_deployed = _read_manifest_at_ref(workspace, "refs/remotes/origin/gh-pages")
        refreshed = merge_manifests(candidate, latest_deployed)
        _write_worktree_manifest(workspace, refreshed)
        _run_git(workspace, "add", "--", "docs/versions.js")
        _commit_staged(workspace, "Update API doc version history")

    raise GitCommandError("gh-pages push retries were exhausted")


def _environment_path(name: str, default: Path) -> Path:
    value = os.environ.get(name)
    return Path(value).resolve() if value else default.resolve()


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Build and deploy the idnumbers API docs workflow artifact.")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("prepare", help="build selected source and stage the current deploy helper")
    commands.add_parser("deploy", help="deploy the prepared artifact to gh-pages")
    args = parser.parse_args(argv)
    workspace = _environment_path("GITHUB_WORKSPACE", Path.cwd())
    runner_temp = _environment_path("RUNNER_TEMP", Path.cwd() / ".docs-runner-temp")
    try:
        if args.command == "prepare":
            prepare(
                workspace,
                runner_temp,
                os.environ.get("IDNUMBERS_DOCS_VERSION", ""),
                os.environ.get("IDNUMBERS_DOCS_SOURCE_REF", ""),
                os.environ.get("IDNUMBERS_DOCS_CALLER_SHA", ""),
            )
        else:
            deploy_workspace(workspace, runner_temp)
    except DocsRebuildError as error:
        print("Documentation rebuild failed: {}".format(error), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
