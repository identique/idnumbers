"""The uppercase country modules must re-export their classes explicitly (``from .x import Name as Name``).

The package ships ``py.typed`` and is checked with ``mypy --strict``, which disallows implicit re-exports. Without the
redundant alias form (PEP 484), a consumer's ``from idnumbers.nationalid.AUS import MedicareNumber`` is a type error.
The alias changes nothing at runtime.
"""

import ast
from pathlib import Path
from typing import List, Tuple
from unittest import TestCase

NATIONALID_DIR = Path(__file__).resolve().parents[1] / "idnumbers" / "nationalid"
MIN_MODULES = 70


def implicit_reexports(tree: ast.Module) -> List[Tuple[int, str, str]]:
    """Return ``(lineno, module_text, name)`` for each single-dot relative import not written ``Name as Name``.

    ``module_text`` is the ``.``-prefixed module (``.chn.resident_id``), or ``.`` for ``from . import name``. The
    ``.util`` import is exempt, and ``..`` or absolute imports are not checked.
    """
    found: List[Tuple[int, str, str]] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.ImportFrom) or node.level != 1 or node.module == "util":
            continue
        module_text = "." + (node.module or "")
        for alias in node.names:
            if alias.asname != alias.name:
                found.append((node.lineno, module_text, alias.name))
    return found


class TestExplicitReexports(TestCase):
    def test_country_modules_reexport_with_redundant_alias(self) -> None:
        modules = sorted(NATIONALID_DIR.glob("[A-Z][A-Z][A-Z].py"))
        self.assertGreaterEqual(len(modules), MIN_MODULES)
        for path in modules:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            for lineno, module_text, name in implicit_reexports(tree):
                with self.subTest(file=path.name, name=name):
                    self.fail(
                        f"{path.name}:{lineno}: import {name!r} from {module_text} "
                        f"must be written '{name} as {name}'"
                    )

    def test_checker_flags_only_single_dot_implicit_reexports(self) -> None:
        def check(source: str) -> List[Tuple[int, str, str]]:
            return implicit_reexports(ast.parse(source))

        # Flagged: the plain form, for both ``from .module import`` and ``from . import``.
        self.assertEqual(
            check("from .chn.resident_id import ResidentID"),
            [(1, ".chn.resident_id", "ResidentID")],
        )
        self.assertEqual(check("x = 1\nfrom . import x"), [(2, ".", "x")])
        self.assertEqual(
            check("from .a import B as B, C"),
            [(1, ".a", "C")],
        )
        # An alias that differs from the name is still not the redundant form.
        self.assertEqual(check("from .a import B as C"), [(1, ".a", "B")])
        # Not flagged: the redundant alias form.
        self.assertEqual(check("from .chn.resident_id import ResidentID as ResidentID"), [])
        self.assertEqual(check("from . import x as x"), [])
        # Exempt: the .util import.
        self.assertEqual(check("from .util import alias_of"), [])
        # Out of scope, so not flagged: two-dot and absolute imports.
        self.assertEqual(check("from ..util import y"), [])
        self.assertEqual(check("from ..x import Y"), [])
        self.assertEqual(check("import os"), [])
        self.assertEqual(check("from os import path"), [])
