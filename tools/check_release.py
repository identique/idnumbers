"""Fail-closed release input and built-artifact checks (no publication)."""
import argparse
import os
from email.parser import BytesParser
from pathlib import Path
import re
import tarfile
from typing import Optional
import zipfile


class ReleaseError(ValueError):
    """A release does not match its approved inputs."""


def check_version(raw: str, expected: str, ref: str, production: bool,
                  trusted: bool) -> str:
    """Allow one stable version line and, when present, its matching v tag."""
    version = raw.removesuffix('\n')
    if re.fullmatch(r'(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)', version) is None:
        raise ReleaseError('VERSION must contain one stable X.Y.Z version')
    if expected and expected != version:
        raise ReleaseError('expected-version does not match VERSION')
    if ref.startswith('refs/tags/') and ref != f'refs/tags/v{version}':
        raise ReleaseError('release tag must equal vVERSION')
    if trusted and not production:
        raise ReleaseError('trusted publishing is prepared only for production')
    return version


def check_artifacts(directory: Path, version: str) -> None:
    """Require exactly one wheel and one sdist with matching package metadata."""
    files = sorted(directory.iterdir())
    wheels = [p for p in files if p.name.endswith('.whl')]
    sdists = [p for p in files if p.name.endswith('.tar.gz')]
    if len(files) != 2 or len(wheels) != 1 or len(sdists) != 1:
        raise ReleaseError('release requires exactly one wheel and one sdist')
    with zipfile.ZipFile(wheels[0]) as wheel:
        names = [n for n in wheel.namelist() if n.endswith('.dist-info/METADATA')]
        if len(names) != 1:
            raise ReleaseError('wheel must have exactly one METADATA')
        wheel_metadata = wheel.read(names[0])
    with tarfile.open(sdists[0], 'r:gz') as sdist:
        members = [m for m in sdist.getmembers()
                   if m.name.count('/') == 1 and m.name.endswith('/PKG-INFO')]
        if len(members) != 1:
            raise ReleaseError('sdist must have exactly one root PKG-INFO')
        stream = sdist.extractfile(members[0])
        if stream is None:
            raise ReleaseError('sdist PKG-INFO must be a file')
        with stream:
            sdist_metadata = stream.read()
    for data in (wheel_metadata, sdist_metadata):
        metadata = BytesParser().parsebytes(data)
        if metadata.get_all('Name') != ['idnumbers'] or metadata.get_all('Version') != [version]:
            raise ReleaseError('artifact package name/version does not match idnumbers VERSION')


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--version-file', type=Path, default=Path('VERSION'))
    parser.add_argument('--expected-version', default=os.environ.get('EXPECTED_VERSION', ''))
    parser.add_argument('--ref', default=os.environ.get('GITHUB_REF', ''))
    parser.add_argument('--to-prod', default=os.environ.get('TO_PROD', 'no'))
    parser.add_argument('--trusted', choices=('true', 'false'),
                        default=os.environ.get('TRUSTED_PUBLISHING', 'false'))
    parser.add_argument('--dist', type=Path)
    args = parser.parse_args(argv)
    try:
        version = check_version(args.version_file.read_text(encoding='utf-8'),
                                args.expected_version, args.ref, args.to_prod == 'yes',
                                args.trusted == 'true')
        if args.dist is not None:
            check_artifacts(args.dist, version)
        output = os.environ.get('GITHUB_OUTPUT')
        if output:
            with open(output, 'a', encoding='utf-8') as stream:
                stream.write(f'version={version}\n')
        print(f'Checked release version {version}')
    except (ValueError, OSError, tarfile.TarError, zipfile.BadZipFile) as error:
        parser.exit(1, f'Release guard failed: {error}\n')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
