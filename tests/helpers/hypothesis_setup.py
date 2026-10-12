"""Keep ancillary Hypothesis caches out of the checkout.

``database=None`` disables the example database, not Unicode/constant caches.
Respect a nonempty contributor storage override; otherwise use temporary storage
cleaned at process exit. Restore the environment immediately after initialization.
"""

import atexit
import importlib
import os
from tempfile import TemporaryDirectory
from types import ModuleType


def load_hypothesis() -> ModuleType:
    original_storage = os.environ.get("HYPOTHESIS_STORAGE_DIRECTORY")
    if original_storage:
        return importlib.import_module("hypothesis")
    storage = TemporaryDirectory(prefix="idnumbers-hypothesis-")
    atexit.register(storage.cleanup)
    os.environ["HYPOTHESIS_STORAGE_DIRECTORY"] = storage.name
    try:
        module = importlib.import_module("hypothesis")
        configuration = importlib.import_module("hypothesis.configuration")
        configuration.set_hypothesis_home_dir(storage.name)
        return module
    finally:
        if original_storage is None:
            del os.environ["HYPOTHESIS_STORAGE_DIRECTORY"]
        else:
            os.environ["HYPOTHESIS_STORAGE_DIRECTORY"] = original_storage


_hypothesis = load_hypothesis()
given = _hypothesis.given
settings = _hypothesis.settings
strategies = importlib.import_module("hypothesis.strategies")
