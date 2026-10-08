# Contributing

`idnumbers` is a dependency-free Python library supporting Python 3.9 and newer. Start with a GitHub issue,
then discuss scope and authoritative sources before changing validity. See [AGENTS.md](AGENTS.md) for project rules
and [the country checklist](docs/COUNTRY_TEMPLATE.md) for new implementations.

## Set up a checkout

Use a Python 3.10+ interpreter for this first environment, which installs the pinned mypy.
Package/runtime support remains Python 3.9+; test that version separately as described below.

```shell
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e . -r requirements-dev.txt
python -m pip install mypy==1.20.2 ruff==0.16.10 coverage==7.16.2 pydoctor==22.9.1
```

Mypy 1.20.2 runs on Python 3.10+ and is pinned because newer major versions cannot target Python 3.9.
Use a separate Python 3.10+ environment for mypy when testing the oldest interpreter.
Optional uv equivalent (choose Python 3.9 to exercise the oldest supported version):

```shell
uv venv --python 3.9
uv pip install -e . -r requirements-dev.txt
uv run python -m unittest
```

Run commands from the checkout root. Standalone scripts can import an installed package rather than this checkout;
use `python -m` or explicitly set `PYTHONPATH` to the checkout for such scripts.

## Local checks

```shell
python -m unittest
python -m unittest tests.nationalid.test_CHN
python -m mypy
python -m mypy --strict tools/scan_ids.py tools/generate_docs.py tools/check_docs_examples.py
ruff check .
python -m coverage run -m unittest
python -m coverage report
python scripts/sync_parity_corpus.py --check
python bench/run.py
python -m tools.check_docs_examples --typecheck
python -m tools.scan_ids --markdown-dir docs/countries --failure-reasons-file docs/FAILURE_REASONS.md --input-formats-file docs/INPUT_FORMATS.md --check
```

Coverage 7.16.2 enforces the 97% floor in `pyproject.toml`; benchmarks are informational. Ruff 0.16.10 uses the
repository's configured rules, not a new formatting policy. CI runs unittest, including generated-guide checks
and executed documentation examples, on Python 3.9–3.14. The existing strict type-check job also checks the tools
and all documentation examples. Keep assertion-based examples independently executable and narrow optional
results explicitly; do not add type ignores to conceal wrong API usage.

For API docs, install pydoctor 22.9.1, use reStructuredText docstrings, and run:

```shell
pydoctor --docformat=restructuredtext --make-html --html-output=docs/_build/apidoc --project-name=idnumbers --project-version=$(cat VERSION) --template-dir=docs/template idnumbers
```

See [API documentation](docs/apidoc.md). Source Markdown guides complement, rather than replace, pydoctor.
Regenerate after metadata or guide-template changes by removing `--check` from the generator command above.
The generator never deletes user files; manually review/remove obsolete marked pages. All samples must be synthetic
or explicitly documented public test vectors, never personal IDs. See [scan tool details](docs/scan_ids.md).

## Fixes and parity

1. Read the issue, the Python implementation and the corresponding Node port implementation.
2. Confirm validity changes against government documentation, an official specification or a well-sourced algorithm.
   Cite the source in the class docstring or `METADATA.links`. The port is a reference, **not an authority**.
3. Add valid and invalid vectors, boundary/format/checksum/date cases, and source notes for real-world public samples.
4. For shared-country validity changes, inspect `tests/parity/expected_python.json`. Regenerate with
   `python scripts/sync_parity_corpus.py`; note changed vectors on the sister port's issue so its parity pin/allowlist
   can be updated. Refresh a vendored port corpus intentionally with
   `python scripts/sync_parity_corpus.py --from-port <port-checkout>`, not to hide a failing expectation.
5. Run the full suite and all checks. Add an entry under the next release in [CHANGELOG.md](CHANGELOG.md).

The sister port is [identique/idnumbers-npm](https://github.com/identique/idnumbers-npm); consult its `docs/PARITY.md`
and `parity/allowlist.json`. Do not blindly copy its algorithms or policies.

## Pull requests and releases

- Every change starts from an issue. Branches are `x<issue>` or `<issue>-<slug>`.
- PR titles are `Fix #<issue> - <description>`; use `WIP #<issue> - <description>` until ready.
- Include `Closes #<issue>` in the description, or `Part of #<issue>` for partial work.
- Keep commits focused and compatibility with Python 3.9. Existing issue templates remain the issue entry points.
- Changes reach `main` through reviewed, squash-merged pull requests; never force-push review branches.
- Do not edit `VERSION` manually or publish without maintainer approval. Follow [release procedure](AGENTS.md#release-procedure)
  and [RELEASE.md](RELEASE.md): changelog PR, version-bump workflow, approved publication, published-package checks,
  then GitHub release.
