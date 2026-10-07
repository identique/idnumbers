"""Installed-distribution smoke checks; run with an isolated interpreter outside the checkout."""

import argparse
import importlib.metadata
from pathlib import Path
import shlex
import subprocess
import sys
import sysconfig


EXAMPLE_OUTPUT = 'Validated and parsed TWN, CHN and ZAF examples.\n'


def check_install(expected_version: str) -> Path:
    import idnumbers

    distribution = importlib.metadata.distribution('idnumbers')
    if distribution.version != expected_version:
        raise RuntimeError('Installed version differs from expected ' + expected_version)
    origin = Path(idnumbers.__file__).resolve()
    installed = Path(distribution.locate_file('idnumbers/__init__.py')).resolve()
    site_dirs = (Path(sysconfig.get_path(name)).resolve() for name in ('purelib', 'platlib'))
    if origin != installed or not any(directory in origin.parents for directory in site_dirs):
        raise RuntimeError('idnumbers was not imported from this interpreter\'s installed distribution: ' + str(origin))
    if Path(sys.prefix).resolve() not in origin.parents:
        raise RuntimeError('idnumbers was not installed in this environment: ' + str(origin))
    if not (origin.parent / 'py.typed').is_file():
        raise RuntimeError('The PEP 561 py.typed marker is missing from the installed idnumbers package: '
                           + str(origin.parent))
    return origin


def readme_code(readme: Path) -> str:
    commands = [shlex.split(line) for line in readme.read_text(encoding='utf-8').splitlines()
                if line.startswith('uvx ')]
    if len(commands) != 1 or commands[0][:5] != ['uvx', '--with', 'idnumbers', 'python', '-c']:
        raise RuntimeError('README uv one-liner changed; update its installed-package check')
    if len(commands[0]) != 6:
        raise RuntimeError('README uv one-liner must contain exactly one Python snippet')
    return commands[0][5]


def check_output(command: list[str], expected: str) -> None:
    result = subprocess.run(command, check=True, capture_output=True, text=True)
    if result.stdout != expected or result.stderr:
        raise RuntimeError('Unexpected example output: ' + repr((result.stdout, result.stderr)))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--version', required=True)
    parser.add_argument('--readme', type=Path, required=True)
    parser.add_argument('--example', type=Path)
    args = parser.parse_args()
    print('Installed idnumbers origin: ' + str(check_install(args.version)))
    if args.example is not None:
        # Direct execution deliberately ignores PEP 723: use the installed wheel, not PyPI.
        check_output([sys.executable, '-I', '-O', str(args.example)], EXAMPLE_OUTPUT)
    check_output([sys.executable, '-I', '-c', readme_code(args.readme)], 'True\n')


if __name__ == '__main__':
    main()
