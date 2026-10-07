"""
A docstring must be the first statement of its function or class.

A string expression that comes later in a function or class body is dead code: Python does not attach it
to anything, so it is missing from `__doc__` and from the generated API documentation.
"""
import ast
import os
from typing import Iterator, List, Tuple
from unittest import TestCase, main

PACKAGE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'idnumbers')
REPO_DIR = os.path.dirname(PACKAGE_DIR)


def _is_string_expr(node: ast.stmt) -> bool:
    return isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant) and isinstance(node.value.value, str)


def _source_files() -> Iterator[str]:
    for root, dirs, files in os.walk(PACKAGE_DIR):
        dirs.sort()
        for name in sorted(files):
            if name.endswith('.py'):
                yield os.path.join(root, name)


def find_misplaced_docstrings(source: str) -> List[Tuple[int, str]]:
    """Return (line, scope name) for every string statement that is not first in a function or class body."""
    offenders = []
    for node in ast.walk(ast.parse(source)):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            continue
        is_class = isinstance(node, ast.ClassDef)
        for index, statement in enumerate(node.body):
            if index == 0 or not _is_string_expr(statement):
                continue
            # a string right after a class attribute is an attribute docstring, which is fine
            if is_class and isinstance(node.body[index - 1], (ast.Assign, ast.AnnAssign)):
                continue
            offenders.append((statement.lineno, node.name))
    return sorted(offenders)


class TestDocstringPlacement(TestCase):
    def test_docstrings_are_first_statements(self) -> None:
        offenders = []
        for path in _source_files():
            with open(path, encoding='utf-8') as source_file:
                source = source_file.read()
            for line, name in find_misplaced_docstrings(source):
                offenders.append(f'{os.path.relpath(path, REPO_DIR)}:{line} {name}')
        self.assertEqual(offenders, [], 'string statements that are not the first statement of their body:\n'
                         + '\n'.join(offenders))


if __name__ == '__main__':
    main()
