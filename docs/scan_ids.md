# Scan IDs tool

We create a new tool for dumping the metadata of all non-alias IDs into JSON.

The tool lists the ID classes through the [country registry](../idnumbers/registry.py) (`list_supported_countries()`),
so it lists every ID class of every country module exactly once. The aliases (such as `NationalID` and `JMBG`) are not
listed, and neither is the shared `idnumbers.nationalid.yugoslavia.UniqueMasterCitizenNumber`, the base class of the
JMBG of the former Yugoslav republics, which has no country. The dump is built from a copy of each `METADATA`, so
running the tool changes nothing in the library.

We could run it with the following command, which takes the package and the path of the JSON file:
```commandline
python -m tools.scan_ids idnumbers.nationalid ids.json
```

The result is a list with one item for each module, and looks like this (shortened to one ID):
```json
[
  {
    "package_name": "idnumbers.nationalid.twn.national_id",
    "country_code": "twn",
    "ids": [
      {
        "class_name": "NationalID",
        "metadata": {
          "iso3166_alpha2": "TW",
          "min_length": 10,
          "max_length": 10,
          "parsable": true,
          "checksum": true,
          "regexp": "^(?P<location>[A-Z])(?P<gender>[12])(?P<sn>\\d{7})(?P<checksum>\\d)$",
          "alias_of": null,
          "names": [
            "National ID Number",
            "\u570b\u6c11\u8eab\u5206\u8b49\u7d71\u4e00\u7de8\u865f",
            "\u8eab\u5206\u8b49\u5b57\u865f"
          ],
          "links": [
            "https://en.wikipedia.org/wiki/National_identification_number#Taiwan",
            "https://zh.wikipedia.org/wiki/%E4%B8%AD%E8%8F%AF%E6%B0%91%E5%9C%8B%E5%9C%8B%E6%B0%91%E8%BA%AB%E5%88%86%E8%AD%89"
          ],
          "deprecated": false,
          "country_name": "Taiwan",
          "id_type": "National Identification Card Number",
          "official_name": "\u570b\u6c11\u8eab\u5206\u8b49\u7d71\u4e00\u7de8\u865f",
          "display_format": "L#########",
          "example": "A123456789",
          "checksum_algorithm": "Weighted sum mod 10 (the location letter becomes two digits; weights 1, 9, 8, 7, 6, 5, 4, 3, 2, 1; check = (10 - remainder) mod 10)",
          "masks": [
            "L#########"
          ]
        }
      }
    ]
  }
]
```

`regexp` is the pattern of the compiled regular expression, `masks` is a list and `alias_of` is `None` or the name of
the class. The `country_name`, `id_type`, `official_name`, `display_format`, `example`, `checksum_algorithm` and `masks`
properties are described in [METADATA.md](nationalid/METADATA.md).

We could use the info/JSON to build a reference doc or generating the sample codes.

## Deterministic Markdown guides

From a source checkout, regenerate all country pages and the failure/input guides:

```shell
python -m tools.scan_ids --markdown-dir docs/countries \
  --failure-reasons-file docs/FAILURE_REASONS.md --input-formats-file docs/INPUT_FORMATS.md
```

Append `--check` to compare without writing; missing, changed or stale generated country pages fail.
Unmarked user pages are left alone; no files are deleted. Remove stale managed pages deliberately when
a country is removed. The legacy positional JSON command above remains supported and does not require test helpers.
Markdown generation uses the source checkout's frozen diagnostic matrix; it performs no network requests.

The [country index](countries/README.md) covers every registered non-alias class and all current metadata fields.
The [failure guide](FAILURE_REASONS.md) consumes frozen synthetic witnesses, not guessed diagnostic outputs.
The [input guide](INPUT_FORMATS.md) measures limited primary-example variants, not exhaustive acceptance policies.

Verify every README/documentation Python fence and standalone script independently:

```shell
python -m tools.check_docs_examples
python -m tools.check_docs_examples --typecheck
```

The second command requires installed mypy 1.20.2 and targets Python 3.9 in strict mode; absence or errors fail.
Temporary unique snippet modules avoid cross-document name collisions. Runtime tracebacks retain document
paths and original line numbers; type checking prints a snippet-to-document line map. Unittest executes
all examples and checks generated guides on every supported CI Python version. Build output under
`docs/_build/` is excluded from snippet discovery.
