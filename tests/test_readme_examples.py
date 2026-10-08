"""Every README/documentation Python fence and example script executes on the CI matrix."""
from pathlib import Path
from unittest import TestCase

from tools.check_docs_examples import discover, execute, python_blocks

README = Path(__file__).resolve().parents[1] / 'README.md'


class TestReadmeExamples(TestCase):
    def test_python_blocks_run(self) -> None:
        self.assertEqual(len(python_blocks(README.read_text(encoding='utf-8'))), 8)
        examples = discover()
        self.assertGreaterEqual(len(examples), 118)
        for example in examples:
            with self.subTest(path=example.path, line=example.line):
                execute([example])
