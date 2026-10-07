"""Offline regression coverage for uv documentation and installed-package smoke checks."""

import ast
import contextlib
import importlib.metadata
import io
from pathlib import Path
import runpy
import subprocess
import sys
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest import TestCase, main
from unittest.mock import patch

import idnumbers
from idnumbers.nationalid import CHN, TWN
from tests import uv_install_spec as spec


ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / 'docs/examples/uv_script.py'


class TestUVInstallSpec(TestCase):
    def test_python_39_syntax_and_inline_metadata(self):
        for path in (EXAMPLE, Path(spec.__file__), Path(__file__)):
            ast.parse(path.read_text(encoding='utf-8'), feature_version=9)
        metadata = EXAMPLE.read_text(encoding='utf-8').split('# /// script\n', 1)[1].split('# ///', 1)[0]
        values = {node.targets[0].id: ast.literal_eval(node.value)
                  for node in ast.parse(metadata.replace('# ', '').replace('requires-python', 'requires_python')).body}
        self.assertEqual(values, {'requires_python': '>=3.9', 'dependencies': ['idnumbers']})

    def test_example_success_and_wrong_results(self):
        example = runpy.run_path(str(EXAMPLE))
        with contextlib.redirect_stdout(io.StringIO()) as output:
            example['main']()
        self.assertEqual(output.getvalue(), spec.EXAMPLE_OUTPUT)
        for target, method, result in ((TWN.NationalID, 'validate', False), (CHN.ResidentID, 'parse', None)):
            with self.subTest(method=method), patch.object(target, method, return_value=result):
                with self.assertRaises(RuntimeError):
                    example['main']()

    def test_readme_snippet_is_extracted_not_duplicated(self):
        code = spec.readme_code(ROOT / 'README.md')
        self.assertIn("TWN.NationalID.validate('A123456789')", code)
        with TemporaryDirectory() as directory:
            readme = Path(directory) / 'README.md'
            readme.write_text('uvx --with idnumbers python -c "print(False)"\n', encoding='utf-8')
            self.assertEqual(spec.readme_code(readme), 'print(False)')
            with self.assertRaises(RuntimeError):
                spec.check_output([sys.executable, '-I', '-c', spec.readme_code(readme)], 'True\n')
            for text in ('', 'uvx --with another python -c "print(True)"',
                         'uvx --with idnumbers python -c "print(True)" extra'):
                readme.write_text(text, encoding='utf-8')
                with self.subTest(text=text), self.assertRaises(RuntimeError):
                    spec.readme_code(readme)

    def test_output_rejects_false_extra_text_stderr_and_nonzero(self):
        for stdout, stderr in (('False\n', ''), ('True\nextra\n', ''), ('True\n', 'warning')):
            result = SimpleNamespace(stdout=stdout, stderr=stderr)
            with patch.object(spec.subprocess, 'run', return_value=result), self.assertRaises(RuntimeError):
                spec.check_output(['python'], 'True\n')
        with patch.object(spec.subprocess, 'run', side_effect=subprocess.CalledProcessError(1, 'python')):
            with self.assertRaises(subprocess.CalledProcessError):
                spec.check_output(['python'], 'True\n')

    def test_install_origin_version_and_missing_distribution(self):
        with TemporaryDirectory() as directory:
            prefix = Path(directory)
            site = prefix / 'lib/site-packages'
            installed = site / 'idnumbers/__init__.py'
            distribution = SimpleNamespace(version='1.13.0', locate_file=lambda _: installed)
            with patch.object(spec.sys, 'prefix', str(prefix)), \
                    patch.object(spec.sysconfig, 'get_path', return_value=str(site)), \
                    patch.object(spec.importlib.metadata, 'distribution', return_value=distribution), \
                    patch.object(idnumbers, '__file__', str(installed)):
                self.assertEqual(spec.check_install('1.13.0'), installed.resolve())
                with self.assertRaises(RuntimeError):
                    spec.check_install('0.0.0')
                with patch.object(idnumbers, '__file__', str(ROOT / 'idnumbers/__init__.py')):
                    with self.assertRaises(RuntimeError):
                        spec.check_install('1.13.0')
                distribution.locate_file = lambda _: ROOT / 'idnumbers/__init__.py'
                with patch.object(idnumbers, '__file__', str(ROOT / 'idnumbers/__init__.py')):
                    with self.assertRaises(RuntimeError):
                        spec.check_install('1.13.0')
                distribution.locate_file = lambda _: installed
                with patch.object(spec.sys, 'prefix', str(prefix / 'other-env')):
                    with self.assertRaises(RuntimeError):
                        spec.check_install('1.13.0')
        with patch.object(spec.importlib.metadata, 'distribution',
                          side_effect=importlib.metadata.PackageNotFoundError('idnumbers')):
            with self.assertRaises(importlib.metadata.PackageNotFoundError):
                spec.check_install('1.13.0')


if __name__ == '__main__':
    main()
