"""Release guards and least-privilege workflow regression checks."""
import contextlib
import io
import itertools
import os
from pathlib import Path
import tarfile
import tempfile
import unittest
from unittest.mock import patch
import zipfile

from tools.check_release import ReleaseError, check_artifacts, check_version, main

ROOT = Path(__file__).resolve().parents[1]


class ReleaseGuardTest(unittest.TestCase):
    def test_stable_versions(self):
        for version in ('0.0.0', '1.15.0', '123.456.789'):
            for suffix in ('', '\n'):
                self.assertEqual(check_version(version + suffix, version,
                                 'refs/tags/v' + version, True, True), version)

    def test_invalid_versions(self):
        for raw in ('', '01.2.3', '1.2', '1.2.3rc1', ' 1.2.3', '1.2.3 ',
                    '1.2.3\n\n', '1.2.3\nmalicious=x', '١.2.3', '1.2.3\r\n'):
            with self.subTest(raw=raw), self.assertRaises(ReleaseError):
                check_version(raw, '', 'refs/heads/main', True, False)

    def test_expected_version_and_tags(self):
        for expected, ref in (('1.2.4', ''), ('', 'refs/tags/1.2.3'),
                              ('', 'refs/tags/v1.2.4')):
            with self.assertRaises(ReleaseError):
                check_version('1.2.3', expected, ref, True, False)
        self.assertEqual(check_version('1.2.3', '', 'refs/heads/main', True, False), '1.2.3')

    def test_route_truth_table(self):
        for production, trusted in itertools.product((False, True), repeat=2):
            if trusted and not production:
                with self.assertRaises(ReleaseError):
                    check_version('1.2.3', '', '', production, trusted)
            else:
                self.assertEqual(check_version('1.2.3', '', '', production, trusted), '1.2.3')

    @staticmethod
    def artifacts(directory, wheel_version='1.2.3', sdist_version='1.2.3', name='idnumbers'):
        with zipfile.ZipFile(directory / 'package.whl', 'w') as wheel:
            wheel.writestr('idnumbers.dist-info/METADATA',
                          f'Name: {name}\nVersion: {wheel_version}\n')
        with tarfile.open(directory / 'package.tar.gz', 'w:gz') as sdist:
            data = f'Name: {name}\nVersion: {sdist_version}\n'.encode()
            info = tarfile.TarInfo('idnumbers/PKG-INFO')
            info.size = len(data)
            sdist.addfile(info, io.BytesIO(data))

    def test_artifact_metadata(self):
        for wheel, sdist, name in (('1.2.3', '1.2.3', 'idnumbers'),
                                   ('1.2.4', '1.2.3', 'idnumbers'),
                                   ('1.2.3', '1.2.4', 'idnumbers'),
                                   ('1.2.3', '1.2.3', 'other')):
            with tempfile.TemporaryDirectory() as temp:
                directory = Path(temp)
                self.artifacts(directory, wheel, sdist, name)
                if wheel == sdist == '1.2.3' and name == 'idnumbers':
                    check_artifacts(directory, '1.2.3')
                else:
                    with self.assertRaises(ReleaseError):
                        check_artifacts(directory, '1.2.3')

    def test_artifact_inventory_and_missing_metadata(self):
        with tempfile.TemporaryDirectory() as temp:
            directory = Path(temp)
            with self.assertRaises(ReleaseError):
                check_artifacts(directory, '1.2.3')
            self.artifacts(directory)
            extra = directory / 'extra.whl'
            extra.touch()
            with self.assertRaises(ReleaseError):
                check_artifacts(directory, '1.2.3')
            extra.unlink()
            with zipfile.ZipFile(directory / 'package.whl', 'w'):
                pass
            with self.assertRaises(ReleaseError):
                check_artifacts(directory, '1.2.3')

    def test_cli_output_and_errors(self):
        with tempfile.TemporaryDirectory() as temp:
            version = Path(temp) / 'VERSION'
            output = Path(temp) / 'output'
            version.write_text('1.2.3\n')
            with patch.dict(os.environ, {'GITHUB_OUTPUT': str(output)}, clear=True):
                with contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(main(['--version-file', str(version)]), 0)
                self.assertEqual(output.read_text(), 'version=1.2.3\n')
                for args in (['--expected-version', '1.2.4'], ['--trusted', 'true'],
                             ['--dist', str(Path(temp) / 'missing')]):
                    with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as error:
                        main(['--version-file', str(version)] + args)
                    self.assertEqual(error.exception.code, 1)
                self.assertEqual(output.read_text(), 'version=1.2.3\n')


class ReleaseWorkflowTest(unittest.TestCase):
    def test_isolated_publishers(self):
        workflow = (ROOT / '.github/workflows/release_to_pypi.yml').read_text()
        self.assertNotIn('release:\n', workflow)
        self.assertIn('default: false', workflow)
        self.assertIn('cancel-in-progress: false', workflow)
        header, build = workflow.split('  build:', 1)
        self.assertNotIn('id-token:', header)
        build = build.split('  publish-token:', 1)[0]
        self.assertNotIn('secrets.', build)
        self.assertNotIn('id-token:', build)
        for job, end, trusted in (('publish-token', 'publish-trusted', False),
                                  ('publish-trusted', 'publish-test', True),
                                  ('publish-test', 'call-docs', False)):
            block = workflow.split(f'  {job}:', 1)[1].split(f'  {end}:', 1)[0]
            self.assertEqual(block.count('pypa/gh-action-pypi-publish@release/v1'), 1)
            self.assertIn('actions/download-artifact@v8', block)
            self.assertNotIn('checkout', block)
            self.assertNotIn('run:', block)
            self.assertEqual('id-token: write' in block, trusted)
            self.assertEqual('password:' not in block, trusted)
            self.assertIn(f'attestations: {str(trusted).lower()}', block)
        self.assertIn('repository-url: https://test.pypi.org/legacy/', workflow)
        docs = workflow.split('  call-docs:', 1)[1]
        self.assertIn("needs.publish-token.result == 'success' || needs.publish-trusted.result == 'success'", docs)
        self.assertIn('always() && !cancelled()', docs)
        self.assertIn('version: ${{ needs.build.outputs.version }}', docs)

    def test_publisher_route_matrix(self):
        workflow = (ROOT / '.github/workflows/release_to_pypi.yml').read_text()
        conditions = {}
        for job in ('publish-token', 'publish-trusted', 'publish-test'):
            condition = workflow.split(f'  {job}:', 1)[1].split('    if: ', 1)[1].split('\n', 1)[0]
            condition = condition.replace('inputs.to-prod', 'target').replace('inputs.trusted-publishing', 'trusted')
            condition = condition.replace('!trusted', 'not trusted').replace('&&', 'and')
            conditions[job] = condition
        for target, trusted, expected in (
                ('yes', False, ['publish-token']), ('yes', True, ['publish-trusted']),
                ('no', False, ['publish-test']), ('no', True, []),
                ('YES', False, ['publish-test']), ('', False, ['publish-test'])):
            actual = [job for job, expression in conditions.items()
                      if eval(expression, {'__builtins__': {}}, dict(target=target, trusted=trusted))]
            self.assertEqual(actual, expected)

    def test_docs_success_matrix(self):
        workflow = (ROOT / '.github/workflows/release_to_pypi.yml').read_text()
        expression = workflow.split('  call-docs:', 1)[1].split('    if: >-', 1)[1].split('    permissions:', 1)[0].strip()
        expression = expression.replace('always()', 'True').replace('!cancelled()', 'not cancelled')
        expression = expression.replace('needs.build.result', 'build').replace('needs.publish-token.result', 'token').replace('needs.publish-trusted.result', 'trusted')
        expression = expression.replace('&&', 'and').replace('||', 'or')
        expression = ' '.join(expression.split())
        for build, token, trusted, cancelled in itertools.product(
                ('success', 'failure', 'skipped', 'cancelled'),
                ('success', 'failure', 'skipped', 'cancelled'),
                ('success', 'failure', 'skipped', 'cancelled'), (False, True)):
            actual = eval(expression, {'__builtins__': {}}, dict(build=build, token=token, trusted=trusted, cancelled=cancelled))
            expected = not cancelled and build == 'success' and 'success' in (token, trusted)
            self.assertEqual(actual, expected)
