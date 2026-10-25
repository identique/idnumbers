"""A static inventory of the ID classes and country modules, read from the source tree without importing it.

The library finds its ID types automatically: the registry reads the upper case ``<ISO3>`` modules, and the
discovery helpers of the tests walk the packages. Nothing in the tests therefore needs a hard-coded count. Instead,
the tests compare what the running library enumerates with this inventory, so a class that is lost (a missing
re-export, a renamed module) or an extra one (a class that no ``<ISO3>`` module exposes) fails by name.

The scan only parses files with ``ast``. It must not import ``idnumbers``: an import would run the same discovery
code that the tests check, and a scan that shares its blind spots with the code under test proves nothing.

The ``MIN_*`` floors are deliberately coarse. They only guard the scan itself against matching nothing (for example
after a directory rename), so they never need an edit when an ID type or a country is added.
"""

import ast
from functools import lru_cache
from pathlib import Path
from typing import FrozenSet, List

REPO_ROOT = Path(__file__).resolve().parents[2]
NATIONALID_DIR = REPO_ROOT / "idnumbers" / "nationalid"
PACKAGE_PREFIX = "idnumbers.nationalid."

SHARED_BASE_CLASSES = frozenset({"idnumbers.nationalid.yugoslavia.UniqueMasterCitizenNumber"})
"""
ID classes that are defined with a ``METADATA`` but that no country registers: the Yugoslav JMBG base that BIH, MKD,
MNE, SRB and SVN subclass.
"""

MIN_COUNTRIES = 80
MIN_ID_TYPES = 100
MIN_PARSABLE_PRIMARIES = 40


def _assigns_metadata(node: ast.ClassDef) -> bool:
    for statement in node.body:
        if isinstance(statement, ast.Assign):
            targets: List[ast.expr] = list(statement.targets)
        elif isinstance(statement, ast.AnnAssign):
            targets = [statement.target]
        else:
            continue
        if any(isinstance(target, ast.Name) and target.id == "METADATA" for target in targets):
            return True
    return False


def _module_name(path: Path) -> str:
    relative = path.relative_to(NATIONALID_DIR).with_suffix("")
    parts = list(relative.parts)
    if parts[-1] == "__init__":
        parts.pop()
    return PACKAGE_PREFIX + ".".join(parts)


@lru_cache(maxsize=None)
def static_id_classes() -> FrozenSet[str]:
    """
    Every top-level class that sets ``METADATA`` in its body, as ``module.ClassName``.

    Only the country packages (``<iso3>/*.py``) and ``yugoslavia.py`` are read. ``util.AliasType`` also has a
    ``METADATA``, but it is the helper behind ``alias_of`` and not an ID type.
    """
    paths = sorted(NATIONALID_DIR.glob("[a-z][a-z][a-z]/*.py"))
    paths.append(NATIONALID_DIR / "yugoslavia.py")
    found = set()
    for path in paths:
        module = _module_name(path)
        for node in ast.parse(path.read_text(encoding="utf-8"), str(path)).body:
            if isinstance(node, ast.ClassDef) and _assigns_metadata(node):
                found.add(module + "." + node.name)
    return frozenset(found)


def registered_id_classes() -> FrozenSet[str]:
    """The ID classes that the registry lists: all of them except the shared base classes."""
    return static_id_classes() - SHARED_BASE_CLASSES


@lru_cache(maxsize=None)
def static_country_modules() -> FrozenSet[str]:
    """The alpha-3 codes of the public country modules, ``idnumbers/nationalid/<ISO3>.py``."""
    return frozenset(path.stem for path in NATIONALID_DIR.glob("[A-Z][A-Z][A-Z].py"))
