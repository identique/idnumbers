"""Exercise Hypothesis storage initialization in isolated interpreter processes."""

import json
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
from typing import Optional
from unittest import TestCase


_STORAGE_ENV = "HYPOTHESIS_STORAGE_DIRECTORY"
_REPO_ROOT = Path(__file__).resolve().parents[1]
_CHILD = """
import json
import os
from pathlib import Path

before = os.environ.get('HYPOTHESIS_STORAGE_DIRECTORY')
from tests.helpers import hypothesis_setup
from hypothesis.configuration import storage_directory
from hypothesis.internal.charmap import charmap, charmap_file

# Force a real ancillary Unicode-cache write, even with the example database disabled.
charmap()
# Python 3.9-compatible Hypothesis returns a Path; newer versions wrap it.
storage = storage_directory()
storage_path = getattr(storage, 'path', storage)
print(json.dumps({
    'before': before,
    'after': os.environ.get('HYPOTHESIS_STORAGE_DIRECTORY'),
    'present': 'HYPOTHESIS_STORAGE_DIRECTORY' in os.environ,
    'storage': str(storage_path.resolve()),
    'cache': str(Path(charmap_file()).resolve()),
    'cache_exists': Path(charmap_file()).is_file(),
}))
"""


class TestHypothesisStorage(TestCase):
    def check_storage(self, override: Optional[str]) -> None:
        with TemporaryDirectory(prefix="idnumbers-storage-test-") as scratch:
            cwd = Path(scratch)
            explicit_storage = cwd / "explicit-storage"
            value = str(explicit_storage) if override else override
            env = os.environ.copy()
            env.pop(_STORAGE_ENV, None)
            if value is not None:
                env[_STORAGE_ENV] = value
            env["PYTHONPATH"] = str(_REPO_ROOT) + os.pathsep + env.get("PYTHONPATH", "")
            result = subprocess.run(
                [sys.executable, "-c", _CHILD],
                cwd=cwd,
                env=env,
                capture_output=True,
                text=True,
                timeout=60,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(result.stdout)
            self.assertEqual(report["before"], value)
            self.assertEqual(report["after"], value)
            self.assertEqual(report["present"], value is not None)
            self.assertTrue(report["cache_exists"])
            storage = Path(report["storage"])
            cache = Path(report["cache"])
            self.assertIn(storage, cache.parents)
            self.assertFalse((cwd / ".hypothesis").exists())
            if override:
                self.assertEqual(storage, explicit_storage.resolve())
                self.assertTrue(storage.is_dir())
                self.assertTrue(cache.is_file())
            else:
                self.assertTrue(storage.name.startswith("idnumbers-hypothesis-"))
                self.assertFalse(storage.exists(), "temporary storage must be cleaned at child exit")
                self.assertFalse(cache.exists())

    def test_unset_override_uses_temporary_storage(self) -> None:
        self.check_storage(None)

    def test_empty_override_uses_temporary_storage(self) -> None:
        self.check_storage("")

    def test_nonempty_override_is_respected(self) -> None:
        self.check_storage("explicit")
