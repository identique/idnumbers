# Generate the API doc for this project

We survey the doc gen tools at the [issue #80](https://github.com/Identique/idnumbers/issues/80). In the end, we
would like to use the simplest tool, [pydoctor](https://pydoctor.readthedocs.io/en/latest/index.html). It generates the api docs based on
[docstring](https://peps.python.org/pep-0257/).

We could run the following script to install:

```shell
python -m virtualenv doc_env
doc_env/bin/activate

pip install pydoctor
```

Use `--docformat=restructuredtext`: the default epytext parser cannot parse shared utility docstring continuations.

And run it:
```shell
pydoctor --docformat=restructuredtext --make-html --html-output=docs/$(cat ./VERSION) --project-name="idnumbers" --project-version=$(cat ./VERSION) --project-url=https://github.com/identique/idnumbers --template-dir=./docs/template idnumbers
```

It outputs the API docs to a folder named `docs/version`. Have fun with it!

## Unified API

`idnumbers.api` implements validation and primary-ID parsing, re-exported by `idnumbers`. `parse_id_info()` calls
`validate()` and consumes its shared `_check()` result, so country lookup, failure reasons and parser exception
handling agree without a second parse call. `ParseIdInfoResult` is a union of frozen `ParseSuccess` and
`ParseFailure` dataclasses, discriminated by the literal `ok` field. It selects only the registry's `NationalID`,
leaving the country-specific classes and their typed `parse()` results unchanged.

The tracked `tests/typing/parse_api_consumer.py` fixture is included in the default strict mypy configuration, so the
CI type-check job checks both discriminator and class-based consumer narrowing as well as package re-exports.
