# Generate the API doc for this project

We survey the doc gen tools at the [issue #80](https://github.com/Identique/idnumbers/issues/80). In the end, we
would like to use the simplest tool, [pydoctor](https://pydoctor.readthedocs.io/en/latest/index.html). It generates the api docs based on
[docstring](https://peps.python.org/pep-0257/).

We could run the following script to install:

```shell
python3 -m venv doc_env
. doc_env/bin/activate

pip install pydoctor==22.9.1
```

Use `--docformat=restructuredtext`: the default epytext parser cannot parse shared utility docstring continuations.

And run it:
```shell
pydoctor --docformat=restructuredtext --make-html --html-output=docs/$(cat ./VERSION) --project-name="idnumbers" --project-version=$(cat ./VERSION) --project-url=https://github.com/identique/idnumbers --template-dir=./docs/template idnumbers
```

It outputs the API docs to a folder named `docs/version`. Have fun with it!

## Rebuild versioned docs from a release tag

The `apidoc` workflow runs from the current `main` workflow definition. To rebuild an older version manually, select
`main` in the workflow dispatch and run:

```shell
gh workflow run docs.yml --ref main -f version=1.22.0 -f source-ref=v1.22.0
```

For a nonempty version, the selected source must contain exactly that stable `X.Y.Z` in `VERSION` (with at most one
final newline). `source-ref` accepts only a matching `vX.Y.Z` tag or its canonical `refs/tags/vX.Y.Z` spelling; it
does not accept branches, arbitrary commits or other refs. With `source-ref` omitted, the workflow uses the exact
caller `github.sha` instead. That default is intentional: the release workflow rebuilds docs before creating its
version tag, so it can deploy from the caller commit without a tag. An empty version builds the development docs from
the caller commit and does not add a `dev` entry to version history.

The current workflow helper and candidate version list remain separate from the selected historical source. The
deploy merges the current candidate with the latest deployed `gh-pages` history, orders stable versions numerically,
and retains entries from concurrent deployments. It replaces only the selected `docs/vX.Y.Z` directory (or `docs/dev`)
and `docs/versions.js`; unrelated deployed files are preserved. Invalid refs, mismatched source versions, malformed
history, fetch/read failures, rebase conflicts or exhausted non-force push retries fail the workflow rather than
silently dropping history.

## Check rendered reference links locally

After the build above with the pinned `pydoctor==22.9.1`, run from the repository root:

```shell
python3 tools/check_api_links.py "docs/$(cat ./VERSION)"
```

The checker uses only the standard library and exits nonzero with the page and expected href if a regression is
found. It checks 12 exact anchor targets inside rendered class and method docstring containers, including complete
parenthesized paths, fragments, the NRIC explicit-target continuation and the Norwegian prose URL without its
surrounding punctuation. Navigation, summary-table links and plain URL text do not count. It does not fetch external
URLs or validate all documentation links. This is a local rendered-output check, not a CI build/check step;
`tests/test_docstring_links.py` continues to check source spelling without a renderer dependency, and
`tests/test_api_links.py` tests the checker using synthetic HTML.

## Unified API

`idnumbers.api` implements validation and primary-ID parsing, re-exported by `idnumbers`. `parse_id_info()` calls
`validate()` and consumes its shared `_check()` result, so country lookup, failure reasons and parser exception
handling agree without a second parse call. `ParseIdInfoResult` is a union of frozen `ParseSuccess` and
`ParseFailure` dataclasses, discriminated by the literal `ok` field. It selects only the registry's `NationalID`,
leaving the country-specific classes and their typed `parse()` results unchanged.

The tracked `tests/typing/parse_api_consumer.py` fixture is included in the default strict mypy configuration, so the
CI type-check job checks both discriminator and class-based consumer narrowing as well as package re-exports.

## Primary-ID formatting

`idnumbers.format` implements `normalize_id()`, `format_id()`, `get_input_mask()` and the frozen `InputMask`,
re-exported by `idnumbers`. The helpers select only the registry primary, never validate, and leave the country
classes unchanged. Formatting is length-only; patterns are case-sensitive whole-input layouts with ASCII letters
and digits (not full validator regexps). In particular, Greek identity-card letters format unchanged but do not
match the ASCII letter pattern. Swedish formatting preserves its significant `+` before the last four digits,
while the metadata masks and pattern retain literal preferred `-` layouts.
See the [README examples](../README.md#primary-id-formatting-and-input-masks) and
[mask metadata](nationalid/METADATA.md). The strict external-consumer fixture
`tests/typing/format_api_consumer.py` is included in the default mypy configuration.

## Source guides and example checks

See the [country index](countries/README.md), [failure reasons](FAILURE_REASONS.md),
[input formats](INPUT_FORMATS.md), and [generator/example commands](scan_ids.md).
These source-checkout Markdown guides complement pydoctor API pages; they are not automatically deployed by pydoctor.
