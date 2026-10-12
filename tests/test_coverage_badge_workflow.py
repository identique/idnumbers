"""Execute the actual badge publisher with a closed fake Git boundary: no real Git or network is used."""

import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest
from typing import Optional

from tests.test_ci_workflow import job_text, steps

SHA = "a" * 40
PAYLOAD = b'{"schemaVersion":1,"label":"coverage","message":"98.31%","color":"brightgreen"}\n'
FAKE_GIT = """
import json
import os
from pathlib import Path
import sys

args = sys.argv[1:]
with open(os.environ["GIT_CALLS"], "a", encoding="utf-8") as log:
    log.write(json.dumps(args) + "\\n")
if args[:1] == ["-c"]:
    assert args[1].startswith("http.extraheader=AUTHORIZATION: basic ")
    args = args[2:]
if args[:1] == ["-C"]:
    args = args[2:]
command = args[0]
if command == "ls-remote":
    assert args[:3] == ["ls-remote", "--exit-code", "--heads"]
    assert args[3] == "https://github.com/identique/idnumbers.git"
    if args[4] == "refs/heads/main":
        sys.stdout.write(os.environ["MAIN_OUTPUT"])
        sys.exit(int(os.environ["MAIN_STATUS"]))
    assert args[4] == "badges"
    sys.exit(int(os.environ["BADGES_STATUS"]))
elif command == "clone":
    assert args[1:5] == ["--quiet", "--depth", "1", "--branch"]
    assert args[5:7] == ["badges", "https://github.com/identique/idnumbers.git"]
    Path(args[7]).mkdir()
elif command == "init":
    assert args[1] == "--quiet"
    Path(args[2]).mkdir()
elif command == "checkout":
    assert args == ["checkout", "--quiet", "--orphan", "badges"]
elif command == "remote":
    assert args == ["remote", "add", "origin", "https://github.com/identique/idnumbers.git"]
elif command == "config":
    assert args[1] in ("user.name", "user.email")
elif command == "add":
    assert args == ["add", "coverage.json"]
elif command == "diff":
    assert args == ["diff", "--cached", "--quiet"]
    sys.exit(1)
elif command == "commit":
    assert args == ["commit", "--quiet", "-m", "chore: update the coverage badge"]
elif command == "push":
    assert args == ["push", "--quiet", "origin", "badges"]
else:
    raise AssertionError("Unexpected Git command: " + repr(args))
"""


def publisher_script() -> str:
    """Extract the literal Bash block from the real publishing step, not a copied implementation."""
    publishing = [step for step in steps(job_text("coverage-badge")) if "Push the badge" in step]
    if len(publishing) != 1:
        raise AssertionError("expected exactly one badge publishing step")
    match = re.search(r"(?ms)^      run: \|\n((?:        .*\n|\n)+)", publishing[0])
    if match is None:
        raise AssertionError("badge publishing step must have a literal run: block")
    return "\n".join(line[8:] for line in match.group(1).splitlines()) + "\n"


class BadgePublisherExecutionTest(unittest.TestCase):
    def run_publisher(
        self, main_status: int = 0, main_output: Optional[str] = None, badges_status: int = 0
    ) -> "tuple[subprocess.CompletedProcess[str], list[list[str]], Optional[bytes]]":
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            fake_bin = root / "bin"
            fake_bin.mkdir()
            fake = fake_bin / "git"
            fake.write_text(f"#!{sys.executable}\n" + FAKE_GIT, encoding="utf-8")
            fake.chmod(0o755)
            calls = root / "calls.jsonl"
            badge = root / "badge"
            badge.mkdir()
            (badge / "coverage.json").write_bytes(PAYLOAD)
            env = dict(os.environ)
            env.update(
                PATH=str(fake_bin) + os.pathsep + os.defpath,
                GITHUB_TOKEN="local-test-token-not-a-secret",
                GITHUB_REPOSITORY="identique/idnumbers",
                GITHUB_SHA=SHA,
                RUNNER_TEMP=str(root),
                GIT_CALLS=str(calls),
                MAIN_STATUS=str(main_status),
                MAIN_OUTPUT=SHA + "\trefs/heads/main\n" if main_output is None else main_output,
                BADGES_STATUS=str(badges_status),
            )
            # All Git invocations resolve to the fake; it never delegates to Git or opens a socket.
            result = subprocess.run(
                ["/bin/bash", "-c", publisher_script()], cwd=root, env=env, capture_output=True, text=True, timeout=20
            )
            recorded = [json.loads(line) for line in calls.read_text(encoding="utf-8").splitlines()]
            published = root / "badges" / "coverage.json"
            return result, recorded, published.read_bytes() if published.exists() else None

    def assert_main_only(self, calls: "list[list[str]]") -> None:
        self.assertEqual(len(calls), 1, "main validation must precede any badges probe or mutation")
        self.assertEqual(calls[0][2:5], ["ls-remote", "--exit-code", "--heads"])
        self.assertEqual(calls[0][-1], "refs/heads/main")

    def test_current_head_publishes_existing_and_missing_badges_without_changing_payload(self) -> None:
        for badges_status in (0, 2):
            with self.subTest(badges_status=badges_status):
                result, calls, payload = self.run_publisher(badges_status=badges_status)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(payload, PAYLOAD)
                self.assertEqual(calls[0][-1], "refs/heads/main")
                self.assertEqual(calls[1][-1], "badges")
                self.assertEqual(calls[-1][2:], ["push", "--quiet", "origin", "badges"])
                self.assertEqual(any("clone" in call for call in calls), badges_status == 0)
                self.assertEqual(any("--orphan" in call for call in calls), badges_status == 2)
                self.assertIn("::add-mask::", result.stdout)
                for call in calls:
                    if any(command in call for command in ("ls-remote", "clone", "push")):
                        self.assertEqual(call[0], "-c")
                    if "config" in call:
                        self.assertIn(call[1], ("user.name", "user.email"))
                    self.assertNotIn("--force", call)
                    self.assertNotIn("-f", call)
                    self.assertFalse(any("local-test-token" in arg for arg in call))

    def test_stale_head_skips_all_badges_operations(self) -> None:
        result, calls, payload = self.run_publisher(main_output="b" * 40 + "\trefs/heads/main\n")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("::notice::", result.stdout)
        self.assert_main_only(calls)
        self.assertIsNone(payload)

    def test_failed_main_probes_preserve_status_without_touching_badges(self) -> None:
        for status in (128, 2):
            with self.subTest(status=status):
                result, calls, payload = self.run_publisher(main_status=status)
                self.assertEqual(result.returncode, status)
                self.assertIn("::error::", result.stdout)
                self.assert_main_only(calls)
                self.assertIsNone(payload)

    def test_empty_malformed_and_multiline_main_records_fail_without_touching_badges(self) -> None:
        for output in (
            "",
            SHA,
            SHA + " refs/heads/main\n",
            "g" * 40 + "\trefs/heads/main\n",
            "a" * 39 + "\trefs/heads/main\n",
            SHA + "\trefs/heads/other\n",
            SHA + "\trefs/heads/main\n" + SHA + "\trefs/heads/main\n",
        ):
            with self.subTest(output=output):
                result, calls, payload = self.run_publisher(main_output=output)
                self.assertEqual(result.returncode, 1)
                self.assertIn("::error::", result.stdout)
                self.assert_main_only(calls)
                self.assertIsNone(payload)

    def test_badges_probe_error_cannot_start_orphan_or_push(self) -> None:
        result, calls, payload = self.run_publisher(badges_status=128)
        self.assertEqual(result.returncode, 128)
        self.assertEqual(len(calls), 2)
        self.assertIn("not touching the badges branch", result.stdout)
        self.assertIsNone(payload)
