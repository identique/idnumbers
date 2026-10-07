# AGENTS.md

Instructions for coding agents and contributors working on `idnumbers`.

## Project overview

This repository is the Python library [`idnumbers`](https://pypi.org/project/idnumbers/). It validates and parses
national ID numbers for many countries, has no runtime dependencies, and supports Python >= 3.9.

**Sister project:** the Node.js/TypeScript port lives at
[identique/idnumbers-npm](https://github.com/identique/idnumbers-npm) (npm `idnumbers`).

- The port was ported from this repo and has since fixed several bugs and added features.
- Its differential parity check compares the two libraries' validity for the shared countries; see the port's
  `docs/PARITY.md`. Known divergences are listed with their tracking issues in its `parity/allowlist.json`.
- Use the port as a **reference, not an authority**. Every validity fix here must be justified by an authoritative
  source: an official spec, government documentation, or a well-sourced algorithm description. Cite that source in
  the class docstring or in `METADATA.links`.

## Rules

### Git and pull requests

- **Issue first:** every change starts from a GitHub issue.
- **Pull requests:** changes reach `main` through a pull request, which is squash-merged.
- **Branch name:** include the issue number, for example `244-croatia-tin` (GitHub's **Create a branch** default on
  an issue) or `x244`.
- **PR title:** `Fix #<issue> - <description>`, for example `Fix #244 - link Croatia TIN with OIB for both entity and
  individual`. The squash merge turns it into the commit subject, `Fix #244 - ... (#259)`.
- **Work in progress:** a PR that isn't ready yet is titled `WIP #<issue> - <description>`.
- **Version bumps:** the bump workflow's bot PR is titled `Bump version to <X.Y.Z>`; see the release procedure.

### Releases

Never publish to PyPI without the maintainer's approval.

## Commands

| Task        | Command                                                                  |
| ----------- | ------------------------------------------------------------------------ |
| All tests   | `python3 -m unittest` (CI runs it on every supported Python version)     |
| One country | `python3 -m unittest tests.nationalid.test_CHN`                          |
| Quick check | `PYTHONPATH=$PWD python3 -c "from idnumbers.nationalid import CHN; ..."` |
| Regexp dump | `python3 -m tools.collect_regexp`                                        |
| Docs        | pydoctor with `--docformat=restructuredtext`; see `docs/apidoc.md`       |

- **Import gotcha:** `python3 some_script.py` may import a **pip-installed** `idnumbers` instead of this checkout,
  because `sys.path[0]` is the script's directory. Use `python3 -m` from the repo root, or set `PYTHONPATH` to the
  checkout.
- **Python 3.9 compatibility:** the oldest supported version is 3.9. Don't use `match`, `X | Y` unions at runtime, or
  other 3.10+ syntax.
- **CI:** `.github/workflows/python-test.yml` runs the unittest suite on every supported Python version for pushes and
  PRs to `main`.

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
   port's parity pin and allowlist get updated.
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
5. **GitHub release:** create release `v<X.Y.Z>` titled `Release <X.Y.Z>` on the released commit, with notes from
   the changelog, and tick **Create a discussion for this release** (see `RELEASE.md`).

Both workflows can also be started from the GitHub CLI, which runs the same GitHub Action:
`gh workflow run bump_version.yml -f version=<X.Y.Z>` and `gh workflow run release_to_pypi.yml -f to-prod=yes`.
`RELEASE.md` also describes a manual release from a local machine (`scripts/publish.ps1`), for use only when the
Actions release can't run.
