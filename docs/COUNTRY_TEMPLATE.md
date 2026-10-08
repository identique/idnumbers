# Country implementation checklist

Use this as a workflow template, not a factory or a new public API proposal. Start with an issue and read
[CONTRIBUTING.md](../CONTRIBUTING.md) and [AGENTS.md](../AGENTS.md). Changes to public shapes require approval
before implementation. The Node port is a useful comparison, **not an authoritative validity specification**.

## 1. Establish the rules

Find official government/specification documentation or a well-sourced algorithm description. Record citations
in the class docstring or `METADATA.links`; explain any limits, historic forms and synthetic test-vector construction.
Do not infer a country's validity rules solely from the port, a mask or this template.

## 2. Module contract

Layout placeholders (not executable Python):

```text
idnumbers/nationalid/<iso3>/<id_type>.py  # lowercase country package
idnumbers/nationalid/<ISO3>.py           # public re-exports
 tests/nationalid/test_<ISO3>.py          # unittest vectors
```

- Class methods are `@staticmethod`; `validate()` returns `bool`, never raises, and rejects non-strings, empty
  and malformed input with `False`. Do not coerce integers to strings or lose leading zeroes.
- If parsable, `parse()` returns a typed dictionary on valid input and `None` for the same malformed inputs.
  Use `TypedDict` and native `datetime.date`/shared enums for applicable fields; narrow optional results in callers.
- `checksum()` conventions vary: existing methods return booleans, computed digits/characters or optional values.
  Follow the nearest appropriate implementation and document the return meaning. Do not rewrite existing checksum
  APIs for consistency. For new computed-checksum implementations, name the regexp's captured check field
  `checksum` so generic diagnostics can compare a definite result without guessing.
- Regexps must match the whole input, with ASCII digits. Check `util.validate_regexp()` and the relevant tests;
  do not use Unicode `\d` without `re.ASCII` or rely on `$` alone to exclude trailing newlines.
- Preserve Python 3.9: no runtime `X | Y` unions or `match` statements. Use `Optional`, `Union` and fully typed signatures.
- Reuse helpers in `idnumbers/nationalid/util.py` (Luhn, Verhoeff, weighted modulus, letter conversion, EAN-13)
  and shared enums in `constant.py`; former Yugoslav IDs share `yugoslavia.py`. Add no runtime dependency.

Concrete, independently runnable existing-class usage (not placeholder implementation):

```python
from idnumbers.nationalid.twn.national_id import NationalID

number = NationalID.METADATA.example
assert NationalID.validate(number)
parsed = NationalID.parse(number)
assert parsed is not None
assert parsed['location'] == 'A'
```

## 3. All 18 METADATA fields

Use `IdMetadata` from `idnumbers/nationalid/metadata.py`. See [full definitions](nationalid/METADATA.md),
[generated country examples](countries/README.md), and `tests/test_metadata.py` for constraints.

| Field | Requirement |
| --- | --- |
| iso3166_alpha2 | Uppercase ISO alpha-2 code |
| min_length | Minimum compact/slot length appropriate to this type |
| max_length | Maximum compact/slot length appropriate to this type |
| parsable | Whether this type provides parsing |
| checksum | Whether this type has a checksum |
| regexp | Compiled whole-input ASCII-digit format pattern |
| alias_of | Original class for an alias; `None` for a concrete ID type |
| names | Recognized names of the ID |
| links | Source/reference URLs, including authority for validity rules |
| deprecated | Whether the ID type is deprecated |
| country_name | Registry English country name |
| id_type | English Title Case description |
| official_name | Local-language official name, or `None`; not a duplicate English id_type |
| display_format | Human-readable layout |
| example | Synthetic accepted example in the preferred mask |
| checksum_algorithm | Algorithm description, or `None` if checksum is false |
| masks | Tuple of accepted layouts, preferred first |

Masks use `#` for a digit, `L` for a letter, `X` for an alphanumeric and `*` for non-whitespace. Literal separators
are layouts, not an automatic normalization policy. Ensure the example validates, fits the preferred mask and
validates in every applicable mask; provide another synthetic vector for masks that need different lengths.
The ASCII UI input pattern is not the complete validator language (Greek letters and Swedish plus are examples).
Avoid drive-by changes to existing regexps/masks to make diagnostics or documentation look uniform.

## 4. Public exports and registration

Re-export every concrete class in the uppercase country module. Set its primary `NationalID` using existing
`alias_of(<PrimaryClass>)` conventions; secondary types remain explicitly selected by callers. Add a new country
to `idnumbers/registry.py`'s `_BUILTIN` with alpha-3, alpha-2 and the CLDR English name. Check registry tests;
the unified validate/parse and UI APIs select the primary class only. Do not add a second public registration shape.

## 5. Tests, parity and documentation

- [ ] Add `tests/nationalid/test_<ISO3>.py` valid and invalid vectors, including non-string, empty, surrounding
  whitespace, trailing newline, Unicode digits and unsupported separators/case as appropriate.
- [ ] Test every changed checksum/calendar behavior, boundaries, typed parse output and synthetic metadata masks.
- [ ] Add explicit frozen diagnostic witnesses and notes to `tests/helpers/failure_reason_vectors.json` for new
  classes; never generate expected reasons from `failure_reason()` itself. Date/checksum cells can be unsupported
  or inconclusive, but require honest notes. Do not imply every checksum gets a specific diagnostic.
- [ ] For shared countries, check parity, regenerate Python goldens only for intentional validity changes and
  coordinate port notes/pin/allowlist updates. Cite source/provenance for any public real-world samples.
- [ ] Add runnable examples that assert expected results; keep each Python fence independent with optional narrowing.
  Structural pseudocode must be labelled `text`, not `python`.
- [ ] Regenerate country/failure/input guides and run their `--check`, example execution and strict type checks.
- [ ] Run full unittest, mypy, ruff and coverage checks from CONTRIBUTING; keep the 97% floor.
- [ ] Add CHANGELOG entry, issue-linked branch/PR and review. Do not edit VERSION or publish without approval.
