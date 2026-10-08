# Migration notes

## 1.14 → upcoming 1.15 (currently Unreleased)

Python **3.9+** and **zero runtime dependencies** remain supported. Existing country validators, parsers and
checksums keep their behavior in this migration; the new helpers are optional wrappers, not new acceptance rules.
See [CHANGELOG.md](CHANGELOG.md) for individual changes and historical country-validity fixes.

### Optional unified API

The registry resolves alpha-2 or alpha-3 codes case-insensitively: `get_validator('tw')` returns the primary ID
class and `get_country('TWN')` returns country metadata. Unknown countries return `None`. Country classes and
secondary ID types remain available through the existing country modules.

`validate(country, value)` returns a frozen `ValidationResult`, not a boolean (it is truthy when valid).
Use `.is_valid` for an explicit boolean. `validate_many()` accepts `(country, value)` pairs.
`parse_id_info(country, value)` returns frozen `ParseSuccess` or `ParseFailure`; narrow by `.ok` before accessing
success information. Parsing cannot extract information from every valid ID: `NOT_PARSABLE` is distinct from
invalid input. These unified operations select **only the country's primary `NationalID`**. Australia's primary
is the driver's licence, not Medicare or TFN; Greece's is the identity card, not its tax number. Select the specific
country class for other ID types.

Extracted information is a fresh, shallow dictionary retaining native values such as `datetime.date` and enums.
Frozen result objects do not make nested dictionaries immutable, deep-copy their contents or serialize them to JSON.
Apply your own serialization policy rather than relying on JSON-ready strings.

Failure reasons are **best-effort and non-exhaustive**. Do not make application correctness depend on a particular
invalid number receiving a specific reason; future releases may extend `FailureReason`. Inconclusive checks and
exceptions retain generic `VALIDATION_FAILED` (including the limitations tracked in
[#506](https://github.com/identique/idnumbers/issues/506)). `failure_reason()` also supports explicit secondary
ID classes, without changing their validity rules.

### Optional normalization and display formatting

`normalize_id()`, `format_id()` and `get_input_mask()` also select only the primary ID type. Normalization is
opt-in; it does **not** make country validators accept newly normalized spellings. Formatting checks length rather
than validity. Frozen `InputMask` results describe UI layout, not a complete national validation specification.

Finnish and Swedish `+` characters can carry meaning: do not strip them with a generic separator-removal rule.
Swedish formatting preserves significant `+` in both 10- and 12-digit inputs, while preferred mask patterns remain
literal minus layouts. Patterns describe ASCII uppercase letters and digits; Greece's identity validator also accepts
Greek letters that the formatting/mask patterns do not cover. Always validate separately after UI formatting.

### Typing, metadata and packaging

The package now ships `py.typed` and corrected annotations, with explicit country-class re-exports for strict type
checkers. Existing code that relied on incorrect return annotations or implicit typing may now report caller errors;
review those errors rather than suppressing them. Runtime exports remain available.

`METADATA` is a typed namespace with additional country/type/name/display/example/checksum/mask fields. It is not a
plain dictionary. Alias metadata now uses the named `IdMetadata` representation instead of the former namespace
representation; do not parse its `repr()` or use it as a serialization contract. Access named attributes instead.

Build metadata moved to PEP 621 `pyproject.toml` with an SPDX MIT license. Source builds require **setuptools >=77**,
installed automatically by build-isolated pip/uv. This is a build dependency, not a runtime dependency.

### Release provenance preparation

The release workflow retains the default token route. Trusted Publishing and attestations are opt-in only after
maintainer-managed external setup; no credentials are removed. See [RELEASE.md](RELEASE.md) for the STOP checklist.
