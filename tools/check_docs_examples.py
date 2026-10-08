"""Execute repository Markdown Python fences and example scripts; optionally check strict types."""
import argparse
import contextlib
import io
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Iterable, List, Tuple

ROOT = Path(__file__).resolve().parents[1]
FENCE = re.compile(r'^```python[ \t]*\n(.*?)^```[ \t]*$', re.DOTALL | re.MULTILINE)


@dataclass(frozen=True)
class Example:
    path: Path
    line: int
    source: str


def python_blocks(text: str) -> List[Tuple[int, str]]:
    """Return the first source line and source for each independently runnable fence."""
    return [(text.count('\n', 0, match.start(1)) + 1, match.group(1)) for match in FENCE.finditer(text)]


def discover(root: Path = ROOT) -> List[Example]:
    """Read README, documentation Markdown (excluding builds), and standalone examples."""
    examples = []
    documents = [root / 'README.md'] + sorted(
        path for path in (root / 'docs').rglob('*.md') if '_build' not in path.relative_to(root).parts
    )
    for path in documents:
        for line, source in python_blocks(path.read_text(encoding='utf-8')):
            examples.append(Example(path, line, source))
    for path in sorted((root / 'docs' / 'examples').glob('*.py')):
        examples.append(Example(path, 1, path.read_text(encoding='utf-8')))
    return examples


def execute(examples: Iterable[Example]) -> None:
    """Execute with fresh globals and original source locations; assertion failures propagate."""
    for example in examples:
        code = compile('\n' * (example.line - 1) + example.source, str(example.path), 'exec')
        with contextlib.redirect_stdout(io.StringIO()):
            exec(code, {'__name__': '__main__', '__file__': str(example.path)})


def typecheck(examples: Iterable[Example], root: Path = ROOT) -> None:
    """Require installed mypy; check each isolated source as a unique strict Python 3.9 module."""
    with TemporaryDirectory(prefix='idnumbers-docs-') as directory:
        paths = []
        for index, example in enumerate(examples):
            path = Path(directory) / f'example_{index:04d}.py'
            path.write_text('\n' * (example.line - 1) + example.source, encoding='utf-8')
            paths.append(str(path))
            print(f'{path.name}: {example.path}:{example.line}')
        environment = dict(os.environ)
        environment['MYPYPATH'] = str(root)
        subprocess.run(
            [sys.executable, '-m', 'mypy', '--strict', '--python-version', '3.9',
             '--follow-imports=normal', *paths], cwd=root, env=environment, check=True,
        )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--typecheck', action='store_true', help='also require strict mypy checks')
    args = parser.parse_args()
    examples = discover()
    execute(examples)
    print(f'Executed {len(examples)} independent documentation examples.')
    if args.typecheck:
        typecheck(examples)


if __name__ == '__main__':
    main()
