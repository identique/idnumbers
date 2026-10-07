"""Keep ancillary Hypothesis caches out of the checkout.

``database=None`` disables the example database, not Unicode/constant caches.
Respect an explicit contributor storage override; otherwise use temporary storage
cleaned at process exit. Restore the environment immediately after initialization.
"""
import atexit
import importlib
import os
from tempfile import TemporaryDirectory
from types import ModuleType


def load_hypothesis() -> ModuleType:
    if 'HYPOTHESIS_STORAGE_DIRECTORY' in os.environ:
        return importlib.import_module('hypothesis')
    storage = TemporaryDirectory(prefix='idnumbers-hypothesis-')
    atexit.register(storage.cleanup)
    os.environ['HYPOTHESIS_STORAGE_DIRECTORY'] = storage.name
    try:
        module = importlib.import_module('hypothesis')
        configuration = importlib.import_module('hypothesis.configuration')
        configuration.set_hypothesis_home_dir(storage.name)
        return module
    finally:
        del os.environ['HYPOTHESIS_STORAGE_DIRECTORY']


_hypothesis = load_hypothesis()
given = _hypothesis.given
settings = _hypothesis.settings
strategies = importlib.import_module('hypothesis.strategies')
