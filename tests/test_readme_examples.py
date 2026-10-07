"""Run every ```python block of README.md, so the documented examples cannot rot."""

import contextlib
import io
import re
from pathlib import Path
from typing import List, Tuple
from unittest import TestCase

README = Path(__file__).resolve().parents[1] / "README.md"
FENCE = re.compile(r"^```python[ \t]*\n(.*?)^```[ \t]*$", re.DOTALL | re.MULTILINE)


def python_blocks(text: str) -> List[Tuple[int, str]]:
    """Return ``(first line number, source)`` for each ```python fenced block, in document order."""
    return [(text.count("\n", 0, m.start(1)) + 1, m.group(1)) for m in FENCE.finditer(text)]


class TestReadmeExamples(TestCase):
    def test_python_blocks_run(self) -> None:
        blocks = python_blocks(README.read_text(encoding="utf-8"))
        self.assertGreaterEqual(len(blocks), 2)
        for index, (line, source) in enumerate(blocks):
            with self.subTest(block=index, line=line):
                code = compile(source, f"README.md:{line}", "exec")
                stdout = io.StringIO()
                with contextlib.redirect_stdout(stdout):
                    exec(code, {"__name__": "__main__"})
                self.assertTrue(stdout.getvalue().strip(), "the example printed nothing")
