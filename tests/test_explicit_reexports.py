"""The uppercase country modules must re-export their classes explicitly (``from .x import Name as Name``).

The package ships ``py.typed`` and is checked with ``mypy --strict``, which disallows implicit re-exports. Without the
redundant alias form (PEP 484), a consumer's ``from idnumbers.nationalid.AUS import MedicareNumber`` is a type error.
The alias changes nothing at runtime.
"""

import ast
from pathlib import Path
from unittest import TestCase

NATIONALID_DIR = Path(__file__).resolve().parents[1] / "idnumbers" / "nationalid"
MIN_MODULES = 70


class TestExplicitReexports(TestCase):
    def test_country_modules_reexport_with_redundant_alias(self) -> None:
        modules = sorted(NATIONALID_DIR.glob("[A-Z][A-Z][A-Z].py"))
        self.assertGreaterEqual(len(modules), MIN_MODULES)
        for path in modules:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            for node in ast.walk(tree):
                if not isinstance(node, ast.ImportFrom) or node.level != 1 or node.module == "util":
                    continue
                for alias in node.names:
                    with self.subTest(file=path.name, name=alias.name):
                        self.assertEqual(
                            alias.asname,
                            alias.name,
                            f"{path.name}:{node.lineno}: import {alias.name!r} from .{node.module} "
                            f"must be written '{alias.name} as {alias.name}'",
                        )
