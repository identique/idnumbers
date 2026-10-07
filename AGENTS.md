# AGENTS.md

Instructions for coding agents and contributors working on `idnumbers`.

This file is the single source of truth. `CLAUDE.md` only imports it (`@AGENTS.md`), so edit the rules here, never in
`CLAUDE.md`. Personal, machine-specific notes belong in an untracked `CLAUDE.local.md`, which is never committed.

## Project overview

This repository is the Python library [`idnumbers`](https://pypi.org/project/idnumbers/). It validates and parses
national ID numbers for many countries, has no runtime dependencies, and supports Python >= 3.9.

**Sister project:** the Node.js/TypeScript port lives at
[identique/idnumbers-npm](https://github.com/identique/idnumbers-npm) (npm `idnumbers`).

- The port was ported from this repo and has since fixed several bugs and added features.
- Its differential parity check compares the two libraries' validity for the shared countries; see the port's
  `docs/PARITY.md`. Known divergences are listed with their tracking issues in its `parity/allowlist.json`.
- The port's `parity/corpus.json` is vendored in `tests/parity/` at a pinned port commit, with Python's own results in
  `tests/parity/expected_python.json`; refresh both with `scripts/sync_parity_corpus.py --from-port <port checkout>`.
- Use the port as a **reference, not an authority**. Every validity fix here must be justified by an authoritative
  source: an official spec, government documentation, or a well-sourced algorithm description. Cite that source in
  the class docstring or in `METADATA.links`.

## Rules

### Git and pull requests

- **Issue first:** every change starts from a GitHub issue.
- **Pull requests:** changes reach `main` through a pull request, which is squash-merged.
- **Branch name:** `x<issue>` (for example `x244`) or `<issue>-<slug>` (for example `38-id-number-for-bulgaria`, the
  name GitHub suggests under **Create a branch** on an issue).
- **PR title:** `Fix #<issue> - <description>`, for example `Fix #244 - link Croatia TIN with OIB for both entity and
  individual`. The squash merge turns it into the commit subject, `Fix #244 - ... (#259)`.
- **Link the issue:** the PR description must contain `Closes #<issue>`. That links the PR to the issue on GitHub and
  closes the issue when the PR merges. A PR that only partly addresses an issue says `Part of #<issue>` instead: the PR then shows in the
  issue's timeline, and the issue stays open.
- **Work in progress:** a PR that isn't ready yet is titled `WIP #<issue> - <description>`.
- **Version bumps:** the bump workflow's bot PR is titled `Bump version to <X.Y.Z>`; see the release procedure.

### Releases

Never publish to PyPI without the maintainer's approval.

## Commands

| Task          | Command                                                                                         |
| ------------- | ----------------------------------------------------------------------------------------------- |
| All tests     | `python3 -m unittest` (CI runs it on every supported Python version)                            |
| One country   | `python3 -m unittest tests.nationalid.test_CHN`                                                 |
| Type check    | `python3 -m mypy` with mypy 1.20.2 on Python >= 3.10 (config in `pyproject.toml`)               |
| Lint          | `ruff check .` with ruff 0.16.10 (rules in `pyproject.toml`)                                    |
| Coverage      | `python3 -m coverage run -m unittest && python3 -m coverage report` (floor in `pyproject.toml`) |
| Benchmarks    | `python3 bench/run.py` (informational)                                                          |
| Parity golden | `python3 scripts/sync_parity_corpus.py` (`--check`, `--from-port <port checkout>`)              |
| Quick check   | `PYTHONPATH=$PWD python3 -c "from idnumbers.nationalid import CHN; ..."`                        |
| Regexp dump   | `python3 -m tools.collect_regexp`                                                               |
| Docs          | pydoctor with `--docformat=restructuredtext`; see `docs/apidoc.md`                              |

### Optional contributor quickstart with uv

With [uv installed](https://docs.astral.sh/uv/getting-started/installation/), run these commands from the repository
root; the plain-Python commands above remain supported:

```bash
uv venv
uv pip install -e .
uv run python -m unittest
uv run python -m unittest tests.nationalid.test_CHN
```

To test the oldest supported Python version, replace the first command with `uv venv --python 3.9` when creating
the environment. The [editable install](https://docs.astral.sh/uv/pip/packages/#editable-packages) uses this checkout.
The two `uv run python -m unittest` commands above run from the repository root and import the checkout, avoiding
the standalone-script import gotcha below. This does not guarantee checkout imports for arbitrary scripts or
working directories.

- **Import gotcha:** `python3 some_script.py` may import a **pip-installed** `idnumbers` instead of this checkout,
  because `sys.path[0]` is the script's directory. Use `python3 -m` from the repo root, or set `PYTHONPATH` to the
  checkout.
- **Python 3.9 compatibility:** the oldest supported version is 3.9. Don't use `match`, `X | Y` unions at runtime, or
  other 3.10+ syntax.
- **CI:** `.github/workflows/python-test.yml` runs the unittest suite (which includes the README example tests) on
  every supported Python version for pushes and PRs to `main`. The same workflow also runs a strict mypy job, a ruff
  lint job, a coverage job that enforces the floor, informational benchmarks and a `ci-summary` job.

## Architecture

- **Country modules:** `idnumbers/nationalid/<iso3>/` (lowercase directory) has one module per ID type, for example
  `chn/resident_id.py` or `aus/medicare.py`.
  - Each class has static `validate()`, `parse()` (when parsable) and `checksum()` methods.
  - Each class also has a `METADATA` `SimpleNamespace` with these fields: `iso3166_alpha2`, `min_length`,
    `max_length`, `parsable`, `checksum`, `regexp`, `alias_of`, `names`, `links` and `deprecated`.
- **Public country modules:** `idnumbers/nationalid/<ISO3>.py` (uppercase) re-exports the classes and defines
  `NationalID = alias_of(<PrimaryClass>)`.
- **Shared helpers:** check these before reimplementing anything.
  - `util.py`: `validate_regexp`, `luhn_digit`, `verhoeff_check`, `weighted_modulus_digit`, `mn_modulus_digit`,
    `modulus_overflow_mod10`, `letter_to_number`, `ean13_digit` and `alias_of`.
  - `constant.py`: `Gender`, `Citizenship` and the other shared enums.
  - `yugoslavia.py`: the JMBG logic shared by BIH, MKD, MNE, SRB and SVN.
- **Country registry:** `idnumbers/registry.py` maps every public country module to its alpha-3 code, alpha-2 code and
  CLDR English name, and `idnumbers` re-exports its functions. A new country module must be added to its `_BUILTIN`
  table; `tests/test_registry.py` fails otherwise.
- **Unified API:** `idnumbers/api.py` has `validate()` / `validate_many()`, which use the registry's `NationalID`;
  `idnumbers` re-exports them.
- **Input contract:** `validate()` never raises. It returns `False` for non-`str`, empty or malformed input, and
  `parse()` returns `None` for the same inputs. Regexps must match the whole input, with ASCII digits only.
- **Tests:** `tests/nationalid/test_<ISO3>.py` (unittest).

## Fixing an issue

1. Read the issue and the matching code in both repos: `idnumbers/nationalid/<iso3>/` here, and
   `src/countries/<iso3>/` in the port.
2. Confirm the fix against an authoritative source. Don't copy the port blindly; it has known bugs of its own, filed
   on `identique/idnumbers-npm`.
3. Add tests for every behaviour change, with both valid and invalid vectors. For real-world vectors, note where they
   come from.
4. If the change alters validity for a country the port shares, note it on `identique/idnumbers-npm`, so that the
   port's parity pin and allowlist get updated. `tests/parity/test_corpus.py` fails when a change alters Python's
   validity on the port's shared parity corpus; regenerate the golden file with
   `python3 scripts/sync_parity_corpus.py` and list the changed vectors in the port note.
5. Run the full suite (`python3 -m unittest`) before pushing.
6. Add the change to `CHANGELOG.md` under the next release.

## Release procedure

Releases run through GitHub Actions and need the maintainer's approval. Don't edit `VERSION` by hand.

1. **Changelog:** merge a PR that moves the release's entries in `CHANGELOG.md` under the new version.
2. **Bump the version:** on GitHub, open **Actions → Bump Release Version with PR → Run workflow** and enter the new
   version (`<X.Y.Z>`).
   - It opens a bot PR that updates `VERSION` and `docs/template/versions.js`.
   - The bot PR is created with `GITHUB_TOKEN`, so CI doesn't run on it. Check that the diff is exactly those two
     files, then merge it.
3. **Publish:** on GitHub, open **Actions → Official Release → Run workflow** and type `yes` in the `to-prod` field.
   - With `yes` it builds the package on GitHub, publishes it to pypi.org, and then deploys the API docs for the new
     version.
   - Any other value publishes to test.pypi.org.
4. **Verify:** check that `https://pypi.org/pypi/idnumbers/json` reports the new version.
5. **Test the published package:** run **Actions → PyPI install test with uv → Run workflow** with `version` set to
   `<X.Y.Z>`. Wait for every Python matrix job to pass before creating the GitHub release. This workflow runs only
   on demand (including after each release), not daily; leaving `version` blank checks the latest PyPI package.
6. **GitHub release:** create release `v<X.Y.Z>` titled `Release <X.Y.Z>` on the released commit, with notes from
   the changelog, and tick **Create a discussion for this release** (see `RELEASE.md`).

The release workflows can also be started from the GitHub CLI, which runs the same GitHub Action:
`gh workflow run bump_version.yml -f version=<X.Y.Z>` and `gh workflow run release_to_pypi.yml -f to-prod=yes`.
Run the published-package check with `gh workflow run pypi-test-cronjob.yml -f version=<X.Y.Z>`.
`RELEASE.md` also describes a manual release from a local machine (`scripts/publish.ps1`), for use only when the
Actions release can't run.
