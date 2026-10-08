"""Documentation tools preserve metadata, deterministic output and strict example checking."""
import contextlib
import io
import json
import os
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch

from idnumbers.registry import list_supported_countries
from tools.check_docs_examples import ROOT, Example, discover, execute, python_blocks, typecheck
from tools.generate_docs import MARKER, cell, country_pages, failure_guide, generate, input_guide, write_files
from tools.scan_ids import collect_ids


class TestGeneratedDocumentation(TestCase):
    def test_complete_deterministic_metadata(self) -> None:
        entries = list_supported_countries()
        classes = [cls for entry in entries for cls in entry.id_types]
        before = [dict(vars(cls.METADATA)) for cls in classes]
        pages = country_pages()
        self.assertEqual(len(entries), 78)
        self.assertEqual(len(classes), 104)
        self.assertEqual(len(pages), 79)
        self.assertEqual(pages, country_pages())
        self.assertEqual(sum(len(python_blocks(source)) for source in pages.values()), 104)
        self.assertEqual(before, [dict(vars(cls.METADATA)) for cls in classes])
        for entry in entries:
            for cls in entry.id_types:
                for key in vars(cls.METADATA):
                    self.assertIn(f'| {key} |', pages[f'{entry.alpha3}.md'])
                self.assertIn(cell(cls.METADATA.regexp.pattern), pages[f'{entry.alpha3}.md'])

    def test_cell_literal_escaping(self) -> None:
        self.assertEqual(cell('a|`<b>\\d\n'), '<code>a&#124;&#96;&lt;b&gt;\\d&#10;</code>')

    def test_checked_in_guides(self) -> None:
        generate(ROOT / 'docs/countries', ROOT / 'docs/FAILURE_REASONS.md', ROOT / 'docs/INPUT_FORMATS.md', True)

    def test_frozen_guide_coverage(self) -> None:
        guide = failure_guide()
        vectors = json.loads((ROOT / 'tests/helpers/failure_reason_vectors.json').read_text())
        self.assertEqual(len(vectors), 104)
        for key, row in vectors.items():
            self.assertIn(key, guide)
            self.assertIn(cell(row['valid']), guide)
            for field in ('checksum', 'birthdate'):
                if row[field] is not None:
                    self.assertIn(cell(row[field]['input']), guide)
                self.assertIn(cell(row[field + '_note']), guide)
        self.assertEqual(guide, failure_guide())
        self.assertEqual(input_guide(), input_guide())
        self.assertIn('CHE, CHL, KOR and USA', input_guide())

    def test_check_missing_changed_stale_and_user_files(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            page = root / 'A.md'
            files = {page: MARKER + '\nA\n'}
            with self.assertRaisesRegex(ValueError, 'missing'):
                write_files(files, True, root)
            write_files(files, False, root)
            first = page.read_bytes()
            write_files(files, False, root)
            self.assertEqual(page.read_bytes(), first)
            (root / 'user.md').write_text('Unmanaged notes')
            write_files(files, True, root)
            page.write_text('drift')
            with self.assertRaisesRegex(ValueError, 'changed'):
                write_files(files, True, root)
            write_files(files, False, root)
            stale = root / 'OLD.md'
            stale.write_text(MARKER + '\nstale')
            with self.assertRaisesRegex(ValueError, 'stale'):
                write_files(files, True, root)
            self.assertTrue(stale.exists())
            with self.assertRaisesRegex(ValueError, 'stale'):
                write_files(files, False, root)
            self.assertTrue(stale.exists())
            self.assertEqual((root / 'user.md').read_text(), 'Unmanaged notes')

    def test_legacy_json_and_cli(self) -> None:
        classes = [cls for entry in list_supported_countries() for cls in entry.id_types]
        before = [dict(vars(cls.METADATA)) for cls in classes]
        with TemporaryDirectory() as directory:
            direct = Path(directory) / 'direct.json'
            cli = Path(directory) / 'cli.json'
            with contextlib.redirect_stdout(io.StringIO()):
                collect_ids('idnumbers.nationalid', str(direct))
            subprocess.run([sys.executable, '-m', 'tools.scan_ids', 'idnumbers.nationalid', str(cli)],
                           cwd=ROOT, check=True, capture_output=True)
            self.assertEqual(direct.read_bytes(), cli.read_bytes())
            rows = json.loads(direct.read_text())
            self.assertEqual(sum(len(row['ids']) for row in rows), 104)
            for row in rows:
                for item in row['ids']:
                    self.assertIsInstance(item['metadata']['regexp'], str)
                    self.assertIsInstance(item['metadata']['masks'], list)
        self.assertEqual(before, [dict(vars(cls.METADATA)) for cls in classes])

    def test_installed_tree_without_tests_preserves_json_and_country_tools(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            # Copy only tracked package/tool sources, as a wheel excludes the tests package.
            tracked = subprocess.run(['/usr/bin/git', 'ls-files', 'idnumbers', 'tools'], cwd=ROOT,
                                     check=True, capture_output=True, text=True).stdout.splitlines()
            for name in tracked:
                if name.endswith(('.py', 'py.typed')):
                    target = root / name
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes((ROOT / name).read_bytes())
            blocker = """import importlib.abc, sys
class NoTests(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname == 'tests' or fullname.startswith('tests.'):
            raise ImportError('tests intentionally absent')
sys.meta_path.insert(0, NoTests())
"""
            environment = dict(os.environ, PYTHONPATH=str(root))
            direct = blocker + """from tools.scan_ids import collect_ids
collect_ids('idnumbers.nationalid', 'direct.json')
from tools.generate_docs import country_pages, input_guide
assert len(country_pages()) == 79
assert 'Input formats' in input_guide()
"""
            subprocess.run([sys.executable, '-c', direct], cwd=root, env=environment,
                           check=True, capture_output=True)
            cli = blocker + """import runpy
sys.argv = ['tools.scan_ids', 'idnumbers.nationalid', 'cli.json']
runpy.run_module('tools.scan_ids', run_name='__main__')
"""
            subprocess.run([sys.executable, '-c', cli], cwd=root, env=environment,
                           check=True, capture_output=True)
            self.assertEqual((root / 'direct.json').read_bytes(), (root / 'cli.json').read_bytes())

    def test_cli_generation_and_drift_exit(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            command = [sys.executable, '-m', 'tools.scan_ids', '--markdown-dir', str(root / 'countries'),
                       '--failure-reasons-file', str(root / 'failure.md'), '--input-formats-file', str(root / 'input.md')]
            subprocess.run(command, cwd=ROOT, check=True, capture_output=True)
            subprocess.run(command + ['--check'], cwd=ROOT, check=True, capture_output=True)
            (root / 'countries/TWN.md').write_text('drift')
            result = subprocess.run(command + ['--check'], cwd=ROOT, capture_output=True)
            self.assertNotEqual(result.returncode, 0)
            for args in ([], ['idnumbers.nationalid'], ['idnumbers.nationalid', 'ids.json', '--check']):
                result = subprocess.run([sys.executable, '-m', 'tools.scan_ids', *args], cwd=ROOT, capture_output=True)
                self.assertNotEqual(result.returncode, 0)


class TestDocumentationExamples(TestCase):
    def test_fence_discovery_lines_and_isolation(self) -> None:
        source = '# Heading\n\n```python\nx = 1\nassert x == 1\n```\n\n```text\nnot Python\n```\n'
        self.assertEqual(python_blocks(source), [(4, 'x = 1\nassert x == 1\n')])
        execute([Example(Path('one.md'), 4, 'x = 1\n'),
                 Example(Path('two.md'), 8, "assert 'x' not in globals()\n")])

    def test_runtime_failure_source_location(self) -> None:
        with self.assertRaises(AssertionError) as context:
            execute([Example(Path('broken.md'), 19, 'assert False\n')])
        self.assertIsNotNone(context.exception)
        try:
            execute([Example(Path('broken.md'), 19, 'raise RuntimeError("broken")\n')])
        except RuntimeError as error:
            traceback = error.__traceback__
            while traceback.tb_next is not None:
                traceback = traceback.tb_next
            self.assertEqual(traceback.tb_lineno, 19)
            self.assertEqual(traceback.tb_frame.f_code.co_filename, 'broken.md')
        else:
            self.fail('Broken example did not fail')

    def test_discovery_includes_scripts_excludes_builds(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'docs/examples').mkdir(parents=True)
            (root / 'docs/_build').mkdir()
            (root / 'README.md').write_text('```python\nassert True\n```\n')
            (root / 'docs/guide.md').write_text('```python\nassert True\n```\n')
            (root / 'docs/_build/ignore.md').write_text('```python\nassert False\n```\n')
            (root / 'docs/examples/run.py').write_text('assert __name__ == "__main__"\n')
            examples = discover(root)
            self.assertEqual(len(examples), 3)
            execute(examples)

    def test_typecheck_is_strict_isolated_and_failure_propagates(self) -> None:
        examples = [Example(Path('first.md'), 4, 'x: int = 1\n'),
                    Example(Path('second.md'), 9, 'x: str = "two"\n')]
        seen = []

        def inspect(command, **kwargs):
            self.assertIn('--strict', command)
            self.assertIn('3.9', command)
            self.assertTrue(kwargs['check'])
            paths = [Path(arg) for arg in command if arg.endswith('.py')]
            seen.extend(paths)
            self.assertEqual(len(paths), 2)
            self.assertNotEqual(paths[0], paths[1])
            self.assertTrue(paths[0].read_text().startswith('\n\n\nx: int'))
            self.assertTrue(paths[1].read_text().startswith('\n' * 8 + 'x: str'))
            raise subprocess.CalledProcessError(1, command)

        with patch('tools.check_docs_examples.subprocess.run', side_effect=inspect):
            with contextlib.redirect_stdout(io.StringIO()), self.assertRaises(subprocess.CalledProcessError):
                typecheck(examples)
        self.assertTrue(all(not path.exists() for path in seen))
