# Changelog

These changelog notes follow [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

Releases before 1.12.0 are listed on the [GitHub releases page](https://github.com/identique/idnumbers/releases).

## 1.19.0 (2026-10-12)

### Documentation

- **Contributor guide** ([#581](https://github.com/identique/idnumbers/issues/581)): the 120-column rule in
  `AGENTS.md` now applies to new and changed lines, and older long lines are not swept. A URL may also stay whole as a
  single string literal, such as an entry of `METADATA.links`. Code and behavior are unchanged.
- **Failure reasons** ([#578](https://github.com/identique/idnumbers/issues/578)): the country template's checklist
  now asks for a `checksum` group in `METADATA.regexp` whenever `checksum()` returns the check digit or character, so
  `failure_reason()` can report `checksum_mismatch`; a `bool` `checksum()` needs no group. The BGR Unified
  Identification Code note in `docs/FAILURE_REASONS.md` now says that a 13-digit code whose first nine digits fail the
  9-digit check but whose 13th digit is correct stays `validation_failed`, because the group covers only the 13th
  digit. Validity and diagnostics are unchanged.

## 1.18.0 (2026-10-12)

### Changed

- **Failure reasons** ([#506](https://github.com/identique/idnumbers/issues/506)): `METADATA.regexp` of 14
  computed-checksum classes (AUS Medicare Number and Tax File Number, BGR Unified Identification Code, CHL National
  Unique Role Number, COL Unique Personal ID, GRC Tax Identity Number, HKG Hong Kong Identity Card Number, IRN National
  ID Number, ISR Identity Number, JPN My Number, LVA Personal Code, TUR National ID Number, UKR Legal Entity ID Number
  and Taxpayer ID Number) now names the check character(s) with a `checksum` group, so `failure_reason()` reports
  `checksum_mismatch` instead of `validation_failed` for a definite check-character mismatch. The unified
  `validate()` and `parse_id_info()` report it too for the nine classes that are their country's primary ID (CHL, COL,
  HKG, IRN, ISR, JPN, LVA, TUR and the UKR Taxpayer ID Number); they select only the primary ID, so the other five
  (AUS Medicare Number and Tax File Number, BGR Unified Identification Code, GRC Tax Identity Number and UKR Legal
  Entity ID Number) are reached through `failure_reason(id_class, number)`. Accepted and rejected inputs, parsed
  results and `checksum()` values are unchanged. The Australian tax file number's `checksum()` returns a remainder
  rather than a check digit, so a remainder equal to the last digit keeps the generic reason.

### Other fixes

- **Parity sync script** ([#564](https://github.com/identique/idnumbers/issues/564)): construct failed-rollback reports
  before bytecode cleanup and test that a failed restore after `KeyboardInterrupt` or `SystemExit` reports both errors
  and the tracked paths with exit code 2; successful rollback still propagates the original interrupt.
- **Registry tests** ([#566](https://github.com/identique/idnumbers/issues/566)): exercise every slow key lookup path
  in the concurrency helper and check the portable non-iterable alias error fragment without changing registry behavior.
- **Release tests** ([#559](https://github.com/identique/idnumbers/issues/559)): cover rejection of a bare
  mismatched-version dist-info entry and an absolute package path in wheels; release guard behavior is unchanged.

### Documentation

- **Contributor guide** ([#551](https://github.com/identique/idnumbers/issues/551)): AGENTS.md documents the
  120-column line-length convention and its exceptions (whole URLs on their own line, Markdown tables and generated
  guides); the 1.17.0 DOM entry now uses python-stdnum's own wording.
- **Contributor guide** ([#561](https://github.com/identique/idnumbers/issues/561)): specify that the re-export
  exemption applies to `from .util import ...`, not `from . import util`; only the rule's wording changes.
- **Display format** ([#557](https://github.com/identique/idnumbers/issues/557)): clarify that capital-letter field
  names are outside `{...}` and `D` usually denotes a day, with widths and meanings defined per class; formats and
  validity are unchanged.
- **EGY** national ID number ([#555](https://github.com/identique/idnumbers/issues/555)): distinguish the Node
  sister project's reported Luhn failure from its unproven weighted mod-11 hypothesis in the docstring; the research
  note is not an official source, and validity is unchanged.
- **Mask vocabulary** ([#570](https://github.com/identique/idnumbers/issues/570)): explain Sweden's retained `+`
  exception to slot-count matching, with a synthetic layout example; preferred input-mask patterns still use literal
  `-`, and formatting behavior is unchanged.
- **Unified API tests** ([#568](https://github.com/identique/idnumbers/issues/568)): document the hostile
  representation helpers with class docstrings; test behavior is unchanged.

## 1.17.0 (2026-10-12)

### Other fixes

- **Metadata follow-up** ([#540](https://github.com/identique/idnumbers/issues/540)): independently pin metadata
  discovery counts, approved display formats and official names in tests; report JSON scans of modules without ID
  classes as clean CLI usage errors. Clarify length-only formatting, refresh Cyprus government/OECD source links
  and use an official Swedish test personal number in formatting tests. Country validation behaviour is unchanged.
- **Packaging** ([#529](https://github.com/identique/idnumbers/issues/529)): the release check now also rejects a
  wheel entry that is a bare file named `idnumbers` or `idnumbers-<version>.dist-info` rather than a path inside that
  directory; the published wheel is unchanged.
- **Parity sync script** ([#533](https://github.com/identique/idnumbers/issues/533)): when `--from-port` fails and
  restoring the tracked files also fails, both errors are reported and the possibly half-updated files are named;
  tests now cover `drop_bytecode()` and keep the non-git port case from finding an enclosing repository.
- **Unified API** ([#538](https://github.com/identique/idnumbers/issues/538)): `validate()`, `validate_many()` and
  `parse_id_info()` no longer raise when a country's `repr()` returns a `str` subclass whose length or slicing raises;
  the README describes the `error_message` fallbacks.

### Documentation

- **CRI** cédula de identidad ([#515](https://github.com/identique/idnumbers/issues/515)): correct the example's
  provenance to the Node port and add tests for compact, fully hyphenated, mixed and malformed hyphen layouts;
  validity and parsed results are unchanged.
- **DOM** cédula de identidad y electoral ([#519](https://github.com/identique/idnumbers/issues/519)): state the
  exact size of python-stdnum's list of cédulas that "do not match the checksum but are nonetheless valid" (578
  entries: 576 with 11 digits, 2 with 10 digits) and quote that description in the docstring; validity is unchanged.
- **ECU** cédula de identidad ([#521](https://github.com/identique/idnumbers/issues/521)): drop the unsourced RUC
  remark, describe the Gob.EC issue on the third digit 6 as reported validation failures, and cite python-stdnum's
  actual hyphenated example `171430710-3`; validity is unchanged.
- **EGY** national ID number ([#523](https://github.com/identique/idnumbers/issues/523)): attribute the Luhn and
  mod-11 check-digit claims to third-party sources and cite the Node port's research note; the failure-reason guide
  now calls its date witnesses impossible-date witnesses, since not every one has a checksum; validity is unchanged.
- **GTM**, **SAU** ([#527](https://github.com/identique/idnumbers/issues/527)): define the `display_format`
  placeholder letters in the class docstrings, and explain in `docs/nationalid/METADATA.md` that letters other than
  `#` (and, in a few classes, `L`) name per-class fields; formats are unchanged.
- Narrow the AGENTS.md re-export rule to the single-dot relative imports that `tests/test_explicit_reexports.py`
  checks, and unit-test the checker ([#531](https://github.com/identique/idnumbers/issues/531)).
- Say in the `register()` docstring that a non-iterable `aliases` raises `TypeError`, and make the registry
  concurrency tests fail when the registration lock is missing
  ([#535](https://github.com/identique/idnumbers/issues/535)).
- **Unified API** ([#543](https://github.com/identique/idnumbers/issues/543)): render builtin `TypeError` names as
  literals in result-class hash documentation, avoiding unresolved API documentation links; behaviour is unchanged.

## 1.16.0 (2026-10-11)

### Added

- **CRI** cédula de identidad ([#329](https://github.com/identique/idnumbers/issues/329)): add the 9-digit Costa Rica
  identity card number `P-TTTT-AAAA` (province 1-9, tomo, asiento), with optional hyphens and no check digit;
  `parse()` returns the province, its name, the tomo and the asiento. python-stdnum's 10-digit `0P-TTTT-AAAA` form is
  not accepted.
- **DOM** cédula de identidad y electoral ([#330](https://github.com/identique/idnumbers/issues/330)): add the
  11-digit Dominican Republic identity and electoral card number `NNN-NNNNNNN-C` with optional hyphens and a Luhn
  check digit; `parse()` returns the series, the sequence and the check digit. python-stdnum's list of issued numbers
  that fail Luhn is not accepted ([#517](https://github.com/identique/idnumbers/issues/517)).
- **ECU** cédula de identidad ([#331](https://github.com/identique/idnumbers/issues/331)): add the 10-digit Ecuador
  identity card number: province 01-24 or 30 (registered abroad), a third digit 0-6 (4 or 5 for province 30) and a
  mod-10 check digit, with an optional hyphen before the check digit; `parse()` returns the province, the sequence
  number and the check digit.
- **EGY** national ID number ([#332](https://github.com/identique/idnumbers/issues/332)): add the 14-digit Egypt
  national number `CYYMMDDGGSSSSV` (Executive Regulations of the Civil Status Law, Art. 3): century 2 or 3 and a real
  birth date are validated; the governorate code, the serial and the final digit are not (no official code table or
  check-digit algorithm is published). `parse()` returns the birth date, the governorate code, the serial and the
  final digit.

- **GTM** Código Único de Identificación / DPI ([#333](https://github.com/identique/idnumbers/issues/333)): add
  structure-only validation of compact 13-digit CUI numbers (department 01-22, municipality 01-99). `parse()`
  preserves the eight-digit correlative, unverified check digit, department and municipality as strings. No
  checksum or per-department municipality table is enforced; whitespace and separators are rejected.

- **RUS** internal passport ([#334](https://github.com/identique/idnumbers/issues/334)): add structure-only
  validation of a four-digit series and six-digit number, rejecting all-zero fields by maintainer policy.
  Accept only compact ASCII digits, `SSSS NNNNNN` or printed `SS SS NNNNNN` with single ASCII spaces;
  `parse()` preserves series and number as strings. No checksum or issuance/authenticity check is performed.

- **SAU** national ID / Iqama ([#335](https://github.com/identique/idnumbers/issues/335)): add structure-only
  validation of the 10-digit Saudi Arabia national ID and resident identity (Iqama) number: the first digit is 1
  (citizen) or 2 (resident), per the NPHIES Patient profile. `parse()` returns the citizenship. No check digit is
  verified, because the Luhn rule is unconfirmed by any authoritative source; only compact ASCII digits are
  accepted.

### Changed

- **Release workflows** ([#468](https://github.com/identique/idnumbers/issues/468)): update the version-bump and
  documentation actions to Node.js 24 runtimes and pin Ubuntu 24.04, preserving the bot PR and docs deployment
  contracts and the existing release authentication routes.
- **Metadata** ([#501](https://github.com/identique/idnumbers/issues/501)): the official names of COL (NUIP), CYP
  (ΑΦΤ) and IRN (شماره ملی) are corrected against official sources. `display_format` now uses `[...]` for an optional
  part and `{...}` for exactly one of the listed characters, and keeps parentheses as printed characters (BGR, HKG,
  IRL, AUS Medicare and FIN). `docs/nationalid/METADATA.md` documents both, and that `masks` are the preferred layouts
  the class accepts, not necessarily every layout it accepts.
- **Packaging** ([#484](https://github.com/identique/idnumbers/issues/484)): the wheel no longer installs the
  repository's top-level `tools` package or the `<prefix>/version/VERSION` data file; it now ships only the
  `idnumbers` package. The source distribution is unchanged, and the library API is unaffected. The release check
  rejects a wheel with any other top-level entry.

### Other fixes

- **Tests** ([#503](https://github.com/identique/idnumbers/issues/503)): treat an empty Hypothesis storage override
  as unset, keeping ancillary caches in temporary storage while preserving the original environment value.
- **Registry** ([#496](https://github.com/identique/idnumbers/issues/496)): `register()` no longer drops aliases
  passed as a one-shot iterable such as a generator, and `aliases` is now typed `Iterable[str]`; `resolve_country()`,
  and so `get_country()` and `get_validator()`, no longer raises for a `str` subclass that overrides `isascii()` or
  `upper()` or for an object that fakes its `__class__`; `register()` rejects a blank name and gives a missing
  alpha-2 code its own error message.
- **Scan tool** ([#501](https://github.com/identique/idnumbers/issues/501)): `tools.scan_ids.collect_ids()` lists only
  the ID classes defined in its `package_name` argument, which it used to ignore, and raises `ValueError` when the
  package defines none. The default `idnumbers.nationalid` output is unchanged.
- **Unified API** ([#499](https://github.com/identique/idnumbers/issues/499)): `validate()` and `parse_id_info()` no
  longer raise when the country's `repr()` raises or when the exception of a validator or parser can't be turned into
  text, and the unsupported-country message shortens a long country value to 80 characters plus `...`. The
  `ValidationResult` and `ParseSuccess` docs say that a result with parsed data isn't hashable.

### Documentation

- Add a local rendered API href checker and hermetic regressions for complete parenthesized URLs, fragments and
  explicit-target continuations ([#463](https://github.com/identique/idnumbers/issues/463)).

- Document the explicit re-export form for country modules and the pinned coverage version in AGENTS.md
  ([#487](https://github.com/identique/idnumbers/issues/487)).

## 1.15.0 (2026-10-08)

### Added

- Add generated country metadata, failure-reason and input-format guides, executed and strictly typed documentation
  examples, and contributor/country workflow templates
  ([#328](https://github.com/identique/idnumbers/issues/328)).

- Add primary-only `normalize_id()`, `format_id()` and `get_input_mask()` with frozen `InputMask` results.
  Metadata-driven formatting checks length, not validity; input patterns use ASCII uppercase letters/digits.
  Swedish formatting preserves a significant `+` in both 10-digit and 12-digit forms; preferred mask patterns
  remain literal minus layouts. Greece's primary metadata example now uses already-accepted Latin letters;
  Greek validation and formatting remain unchanged ([#321](https://github.com/identique/idnumbers/issues/321)).

- Add `failure_reason(id_class, id_number)` for primary and secondary ID types. Unified validation and parsing now
  report best-effort length, format, checksum and embedded-calendar-date reasons; inconclusive checks and exceptions
  retain `VALIDATION_FAILED`. Date tracing is isolated between nested calls, threads and async tasks, and country
  validity, parser and checksum behavior is unchanged ([#322](https://github.com/identique/idnumbers/issues/322)).

- Add `idnumbers.parse_id_info(country, id_number)` for a country's primary `NationalID`, returning the frozen
  `ParseSuccess` / `ParseFailure` union `ParseIdInfoResult`. The `ok` discriminator supports strict type narrowing;
  success includes a fresh dictionary of the country parser's information. Lookup and validation failures match
  `validate()`, while valid IDs without extractable information give `NOT_PARSABLE`. Country parsers are unchanged
  ([#319](https://github.com/identique/idnumbers/issues/319)).

- Add a country registry, `idnumbers.registry`, which is re-exported from `idnumbers`. `get_validator('tw')`,
  `get_country('TWN')` and `resolve_country('tw')` find the `NationalID` class, a `CountryEntry` (alpha-3 and alpha-2
  code, name, `NationalID` and all ID types) or the alpha-3 code of a country by its alpha-2 or alpha-3 code in any
  letter case, and give `None` for anything unknown instead of raising. `list_supported_countries()` lists the 78
  countries, and `register()` adds a custom country. The names are the English names of Unicode CLDR 48.2.3. AUS and
  GRC keep their current `NationalID`, and a country module is imported on the first lookup of its country
  ([#318](https://github.com/identique/idnumbers/issues/318)).
- Add `idnumbers.validate(country, id_number)`, which validates an ID number of any supported country and returns a
  frozen `ValidationResult` with `is_valid`, the alpha-3 `country_code`, the `id_number`, the `extracted_info` of a
  valid ID number (the `parse()` result, `None` when the ID type isn't parsable), a `reason` and an `error_message`. It
  never raises, and a result is truthy when it is valid. An unknown country gives the reason `unsupported_country`,
  other failures a best-effort diagnostic reason. `validate_many()` validates `(country, id_number)` pairs, and
  `FailureReason` lists the reasons, which later releases may extend. The country classes are unchanged
  ([#317](https://github.com/identique/idnumbers/issues/317)).
- Describe every ID class with seven more `METADATA` keys: `country_name`, `id_type`, `official_name` (`None` for an
  ID with no local-language name), `display_format`, `example` (a synthetic number the class validates),
  `checksum_algorithm` (`None` without a check digit) and `masks`, the layouts the class accepts. `METADATA` is now an
  `IdMetadata`, a typed `SimpleNamespace` subclass in `idnumbers.nationalid.metadata`, so attribute access, `vars()`,
  `copy()` and `getattr()` work as before. A class made by `alias_of`, such as `AUS.NationalID`, now has the name,
  module and docstring of its target instead of `AliasType`, which changes its `repr`. `CAN.SocialInsuranceNumber`
  gets the `deprecated` key the other classes already had, and `tools.scan_ids` lists the classes through the country
  registry ([#320](https://github.com/identique/idnumbers/issues/320)).

### Changed

- Ship the PEP 561 `py.typed` marker, so type checkers use the package's annotations, and correct the annotations
  that disagreed with the runtime values: the `CHECK_DIGIT` alias, the untyped `normalize` and `checksum` helpers,
  the COL and KAZ `checksum` methods that return `False` for malformed input, the AUS TFN and KWT civil-number
  `checksum` methods, which can return 10, and the LTU `extract_year_base_gender` result, which is never `None`
  ([#325](https://github.com/identique/idnumbers/issues/325)).
- Move the build metadata from `setup.py` to a PEP 621 `pyproject.toml`. The license is now the SPDX expression `MIT`
  instead of the deprecated license classifier ([#465](https://github.com/identique/idnumbers/issues/465)), and
  building from source needs setuptools 77 or later, which pip and uv install automatically
  ([#325](https://github.com/identique/idnumbers/issues/325)).
- CI type-checks the package with strict mypy for Python 3.9 and checks the built distributions with
  `twine check --strict` ([#325](https://github.com/identique/idnumbers/issues/325)).
- Re-export the ID classes explicitly (`import X as X`) from the country modules such as `AUS`, so strict type
  checkers (mypy `--strict`, which disallows implicit re-exports) accept
  `from idnumbers.nationalid.AUS import MedicareNumber` and `AUS.MedicareNumber`; nothing changes at runtime
  ([#326](https://github.com/identique/idnumbers/issues/326)).

- Prepare isolated, guarded PyPI publication and opt-in Trusted Publishing with attestations; retain the working
  default token route and existing secrets. External publisher setup and the first verified trusted release remain
  pending maintainer action. Document release ordering and 1.14.0-to-1.15.0 migration
  ([#327](https://github.com/identique/idnumbers/issues/327)).

- Add dev-only Hypothesis checks of arbitrary Unicode inputs for every registered ID type, metadata method
  contracts, out-of-range lengths and checksum mutations, with explicit synthetic witnesses for checksum limits
  ([#324](https://github.com/identique/idnumbers/issues/324)).

- CI lints with ruff, enforces a 97% line-and-branch coverage floor, runs the README Python examples and
  informational benchmarks, keeps GitHub Actions updated with Dependabot, and reports a single `ci-summary` result
  ([#326](https://github.com/identique/idnumbers/issues/326)). Formatting with `ruff format` and a coverage badge
  await a decision in [#485](https://github.com/identique/idnumbers/issues/485).
- Vendor the Node port's parity corpus (78 countries, 17,960 vectors) at a pinned port commit and record Python's own
  validity for it, so a validity change on any shared vector fails a test and gets a port note;
  `scripts/sync_parity_corpus.py` refreshes both ([#323](https://github.com/identique/idnumbers/issues/323)).

## 1.14.0 (2026-10-07)

### Documentation

- Add an optional uv contributor quickstart with editable installation and full-suite or single-country tests
  ([#473](https://github.com/identique/idnumbers/issues/473)).

- Check published PyPI packages with uv on Python 3.9 and 3.14 on demand, and document the post-release check
  ([#472](https://github.com/identique/idnumbers/issues/472)).

- Add a runnable uv script and isolated wheel-install CI checks for the script and README one-liner
  ([#471](https://github.com/identique/idnumbers/issues/471)).

- Document project, virtual-environment, one-off and standalone-script usage with uv in the README
  ([#470](https://github.com/identique/idnumbers/issues/470)).

## 1.13.0 (2026-10-07)

### Validity changes

- **ALB** identity number ([#344](https://github.com/identique/idnumbers/issues/344)): decoded birth dates after today
  are rejected, using the date rather than a fixed decade cap. The existing historical year range is unchanged,
  pending confirmation in [#446](https://github.com/identique/idnumbers/issues/446).
- **ARG** DNI ([#280](https://github.com/identique/idnumbers/issues/280)): 7-digit numbers (below 10 million), such as
  `5.123.456` and `5123456`, are now accepted. `METADATA.min_length` is 7.
- **AUT** entity UID ([#345](https://github.com/identique/idnumbers/issues/345)): require the `U` prefix;
  other letters are rejected by `validate()` and the input guard in `checksum()`, even with a correct
  check digit. The checksum arithmetic and supported separators are unchanged.
- **BRA** CPF ([#284](https://github.com/identique/idnumbers/issues/284)): numbers made of one repeated digit,
  `000.000.000-00` to `999.999.999-99`, are now rejected. They pass the check digits, but the federal civil-registry
  system SIRC lists repeated digits as a reason for an invalid CPF. `checksum()` is unchanged.
- **CHN** resident ID ([#347](https://github.com/identique/idnumbers/issues/347)): accept ASCII lowercase `x` as the
  final check character; parsed and calculated check characters remain canonical `X` or integers. Checksum arithmetic,
  calendar validation and region policy are unchanged; region/issuance checks remain deferred to
  [#451](https://github.com/identique/idnumbers/issues/451).
- **CYP** tax number ([#348](https://github.com/identique/idnumbers/issues/348)): prefix `12` is rejected;
  `checksum()` remains unchanged.
- **DEU** tax ID (IdNr) ([#289](https://github.com/identique/idnumbers/issues/289)): the digit rules now follow the
  ELSTER specification. A leading `0` is rejected, which includes ELSTER test numbers such as `02476291358`. Among the
  first ten digits, exactly one digit must appear twice or three times, so `39825979193` (four 9s) and `36794081522`
  (no repeated digit) are rejected. A check digit equal to the two digits before it is no longer rejected, so
  `38056471999` is now valid.
- **DNK** CPR number ([#290](https://github.com/identique/idnumbers/issues/290)): the century now comes from the
  seventh digit and the two-digit year, as the CPR office's table defines it, instead of `yy > 50`. `parse()` reads
  `0101451234` as 1945-01-01 instead of 2045-01-01, and 1858-1899 births are recognised. `2902000000` (29 February 1900)
  is now rejected and `2902004000` (29 February 2000) is valid. A birth date in the future is rejected.
- **ESP** DNI ([#349](https://github.com/identique/idnumbers/issues/349)): `validate()` and `checksum()` now accept
  ASCII lowercase check letters and strip surrounding whitespace. Checksum arithmetic and the eight-ASCII-digit
  plus ASCII-letter payload format are unchanged; internal whitespace and separators remain invalid.
- **FRA** NIR ([#291](https://github.com/identique/idnumbers/issues/291)): birth department `96` is now accepted. It
  was used for Tunisia before 1964, like 91-95 for Algeria and Morocco, so `145089612304582` is now valid.
- **IDN** NIK ([#293](https://github.com/identique/idnumbers/issues/293)): encoded birth days are now validated as
  `01`-`31` for men and `41`-`71` for women. Impossible dates are rejected, while 29 February with year `00` is
  accepted because it exists in 2000 even though it does not exist in 1900; NIK does not identify the century.
- **IRL** PPS number ([#294](https://github.com/identique/idnumbers/issues/294)): the optional second suffix character
  is now limited to `A`, `B`, `H`, `W` or a space; other letters are rejected even when the check character is correct.
  The whitespace restriction was already fixed in [#369](https://github.com/identique/idnumbers/issues/369).
  Historical `T`/`X` suffix handling remains out of scope and is tracked in
  [#433](https://github.com/identique/idnumbers/issues/433).
- **IRN** national ID ([#295](https://github.com/identique/idnumbers/issues/295)): codes made of one repeated digit,
  `0000000000` to `9999999999`, are now rejected, including supported hyphenated formats. `checksum()` is unchanged.

- **ISR** identity number ([#350](https://github.com/identique/idnumbers/issues/350)): reject `000000000` even though
  it passes Luhn. `checksum()` is unchanged; the exact nine-digit format remains required. Shorter-number padding
  policy is deferred to [#455](https://github.com/identique/idnumbers/issues/455).

- **KAZ** BIN ([#297](https://github.com/identique/idnumbers/issues/297)): registration months outside `01`-`12` are
  now rejected, including checksum-correct `750061381659` (month `00`). `checksum()` is unchanged.
- **LKA** NIC ([#299](https://github.com/identique/idnumbers/issues/299)): both old and new formats now reject encoded
  birth-day values outside `001`-`366` for men and `501`-`866` for women, even with a correct checksum.
  `checksum()` and within-range date decoding are unchanged; leap-year-specific decoding remains out of scope in
  [#437](https://github.com/identique/idnumbers/issues/437).

- **LTU** personal code ([#300](https://github.com/identique/idnumbers/issues/300)): century decoding now accepts
  `50002290013` (29 February 2000) and rejects `70002290015` (29 February 2100). `checksum()` is unchanged.
  First-digit policy for `0` and `9` remains out of scope in [#337](https://github.com/identique/idnumbers/issues/337).

- **LVA** personal code ([#301](https://github.com/identique/idnumbers/issues/301)): legacy codes now require a valid
  calendar date and century digit `0`/`1`/`2`; unsupported prefixes `00` and `40`-`99` are rejected even with a correct
  check digit. Date-free modern prefixes `32`-`39` remain accepted per current primary sources. `checksum()` is
  unchanged; the modern checksum requirement remains out of scope in
  [#440](https://github.com/identique/idnumbers/issues/440).

- **MAC** identity number ([#351](https://github.com/identique/idnumbers/issues/351)): parentheses around the final
  digit must be paired; unbalanced forms are rejected. Compact eight-digit and printed parenthesized forms remain
  accepted, with unchanged parse payloads and eight-significant-digit length metadata.

- **MEX** CURP ([#352](https://github.com/identique/idnumbers/issues/352)): `validate()` and `parse()` reject
  the 81 original inconvenient name prefixes in RENAPO's catalogue. Their second-letter `X` replacements remain
  accepted when otherwise valid; standalone `checksum()` is unchanged.

- **NLD** BSN ([#303](https://github.com/identique/idnumbers/issues/303)): compact nine-digit numbers such as
  `123456782` are now accepted, while the existing fully dotted layout `1234.56.782` remains accepted. All-zero
  numbers remain rejected in both formats; the 11-proof and `checksum()` are unchanged.

- **NZL** ([#306](https://github.com/identique/idnumbers/issues/306)): the expanded NHI checksum now uses modulus
  23 and check-letter indices 1-23, per HISO 10046:2024; the legacy numeric checksum is unchanged. Driver licence
  prefixes now require two ASCII letters, preserving lowercase acceptance and the trailing-digit blacklist. IRD
  numbers must be within the current inclusive 10,000,000-200,000,000 range and pass the existing checksum.

- **PRT** ([#353](https://github.com/identique/idnumbers/issues/353)): add `CitizenCard` for compact 12-character
  document numbers with the full-card checksum. `CivilIDNumber` and `NationalID` remain BI/NIC-only. NIF now accepts
  prefixes `74`, `75`, `77`, `78` and `79`; its checksum arithmetic and other prefix rules are unchanged.

- **SWE** ([#311](https://github.com/identique/idnumbers/issues/311)): personnummer now accepts 10- and 12-digit
  compact forms and optional `-`/`+` separators; explicit four-digit years determine the century. Only the two
  century digits are excluded from the checksum. Add separate `CoordinationNumber` support for samordningsnummer,
  with encoded birth day +60 and decoded dates in `parse()`. `NationalID` remains personnummer-only; existing
  10-digit `-`/`+` decoding and checksum-calculator behavior are unchanged.

- **UKR** EDRPOU ([#312](https://github.com/identique/idnumbers/issues/312)): a second-pass remainder of `10` now
  maps to check digit `0`, so `57334830` and `43089360` are accepted. Existing weight selection is unchanged;
  the separate selection question remains tracked in [#342](https://github.com/identique/idnumbers/issues/342).

### Other fixes

- **ALB** identity number ([#344](https://github.com/identique/idnumbers/issues/344)): the missing metadata comma is
  restored, separating `Numri i Identitetit të Shtetasit` and `NISH` into the intended six names.
- **BGD** national ID ([#346](https://github.com/identique/idnumbers/issues/346)): `parse()` returns `yyyy` as
  the declared four-character string, preserving leading zeros. The national ID metadata lengths are corrected to 17;
  old national ID metadata remains 13.
- **BIH** ([#354](https://github.com/identique/idnumbers/issues/354)): correct the JMBG class country label to
  Bosnia and Herzegovina; validation and parsing are unchanged.
- **CHN** resident ID ([#419](https://github.com/identique/idnumbers/issues/419)): add regression coverage for
  October birth dates, already fixed in [#275](https://github.com/identique/idnumbers/issues/275);
  validity is unchanged.
- **FRA** NIR ([#291](https://github.com/identique/idnumbers/issues/291)): `parse()` now reports gender code `7`, the
  temporary number for a man, as male. Codes `3` and `4` are still reported as female, because no source says which sex
  they stand for ([#429](https://github.com/identique/idnumbers/issues/429)).
- **GRC** ([#354](https://github.com/identique/idnumbers/issues/354)): correct new identity-card length metadata to
  eight significant characters. Old-card metadata remains seven; optional-hyphen validation is unchanged.
- **IDN** NIK ([#293](https://github.com/identique/idnumbers/issues/293)): `parse()` now decodes women's day numbers by
  subtracting 40, reports gender from the encoded day, and always returns `dd` as two digits. The alpha-2 metadata is
  corrected from `IDN` to `ID`.

- **KAZ** BIN ([#297](https://github.com/identique/idnumbers/issues/297)): `parse()` now reports entity code `5` as
  `NonResidentEntity` and code `6` as `IP` (individual entrepreneurs in a joint enterprise), rather than
  `ResidentEntity`. Code `4` remains `ResidentEntity`.

- **KOR** ([#354](https://github.com/identique/idnumbers/issues/354)): clarify that both RRN classes count 13
  significant digits in metadata; validation and parsing still require the hyphenated 14-character layout.
- **LTU** personal code ([#300](https://github.com/identique/idnumbers/issues/300)): `parse()` now maps first digits
  `1`/`2` to the 1800s, `3`/`4` to the 1900s, `5`/`6` to the 2000s and `7`/`8` to the 2100s. Odd digits still
  report male and even digits female; `39001010077` now reports 1990-01-01 instead of 1890-01-01.

- **NZL** passport ([#306](https://github.com/identique/idnumbers/issues/306)): remove the unrelated `NIN` metadata
  name; passport validation is unchanged.

- **PAK** national ID ([#307](https://github.com/identique/idnumbers/issues/307)): correct the alpha-2 metadata from
  `PA` to `PK`; validation and parsing are unchanged.

- **PHL** ([#354](https://github.com/identique/idnumbers/issues/354)): identify the existing 12-digit format as the
  PhilSys Number (PSN), not the 16-digit PhilID Card Number (PCN). Public class names, aliases and validation are
  unchanged.
- **PRT** NIF ([#353](https://github.com/identique/idnumbers/issues/353)): restore the missing metadata comma,
  separating `Número de identificação fiscal` and `NIF` into the intended three names.

- **USA** ([#354](https://github.com/identique/idnumbers/issues/354)): clarify that SSN metadata counts nine
  significant digits; validation still requires the two hyphens in the 11-character printed layout.

- **ZAF** national ID ([#419](https://github.com/identique/idnumbers/issues/419)): add regression coverage for
  October birth dates, already fixed in [#275](https://github.com/identique/idnumbers/issues/275);
  validity is unchanged.

- **Documentation** ([#409](https://github.com/identique/idnumbers/issues/409)): escape closing parentheses in
  docstring URLs so API reference links preserve complete paths and fragments. Validation and metadata are unchanged.

- **Packaging** ([#419](https://github.com/identique/idnumbers/issues/419)): include `CHANGELOG.md` in the source
  distribution; wheel contents are unchanged.

## 1.12.0 (2026-10-07)

The first release since 1.11.0. It fixes validity bugs that were found by comparing the library with its Node.js port
and with python-stdnum. Every fix cites its source in the class docstring or in `METADATA.links`. Several fixes change
which IDs are accepted, so read the first two sections before you upgrade.

### Behaviour changes

- `validate()` never raises any more. It returns `False` for non-`str` input, for empty input and for malformed input,
  and `parse()` returns `None` for the same inputs. Before, most types raised `AssertionError`, `ValueError`,
  `IndexError` or `TypeError` ([#371](https://github.com/identique/idnumbers/pull/371)).
- An integer is no longer converted to a string. ALB, ARE, BHR, CHN, EST, ITA, KWT, LKA (old), LTU, POL and VNM used to
  turn non-`str` input into text with `repr()`, so `LTU.NationalID.validate(37605030299)` was `True`. It is now `False`,
  like every other type. Convert integers with `str()` first ([#371](https://github.com/identique/idnumbers/pull/371)).
- The whole input must match, with ASCII digits only. A trailing newline, and digits such as Arabic-Indic `١٢٣` or
  full-width `１２３`, used to slip through the patterns and are now rejected
  ([#369](https://github.com/identique/idnumbers/pull/369)). The Irish PPS number allows only a space after the number,
  not other whitespace. A tab or newline there used to raise and now gives `False`
  ([#369](https://github.com/identique/idnumbers/pull/369)).
- `checksum()` has a documented contract for malformed input. Checksums that return a digit or letter return `None`, and
  checksums that return a `bool` return `False`, instead of raising or returning a meaningless value:
  - BGR, BRA (CPF and RG), IRN and JPN: `None` or `False` for input that does not match the format. For example,
    `JPN.MyNumber.checksum('00000000178')` was `'3'` and is now `None`
    ([#371](https://github.com/identique/idnumbers/pull/371)).
  - ZAF: `None` for input that does not match the ID format ([#394](https://github.com/identique/idnumbers/pull/394)).
  - TWN: `None` instead of `False` ([#396](https://github.com/identique/idnumbers/pull/396),
    [#414](https://github.com/identique/idnumbers/pull/414)).
  - CHL: `None` instead of raising or returning a meaningless character
    ([#410](https://github.com/identique/idnumbers/pull/410)).
  - ZWE: `False` instead of raising `AttributeError` ([#415](https://github.com/identique/idnumbers/pull/415)).
  - Callers that used `checksum()` to compute a check digit from a prefix that does not match the ID format are
    affected.
- `checksum()` results that were wrong are corrected: TWN returns `0` instead of `10`
  ([#396](https://github.com/identique/idnumbers/pull/396)), BGR EGN returns `0` instead of `10`
  ([#375](https://github.com/identique/idnumbers/pull/375)), and `util.ean13_digit` now weights the even positions by 3
  as EAN-13 does ([#377](https://github.com/identique/idnumbers/pull/377)). CHE `BusinessID` gains a `checksum()` method
  ([#377](https://github.com/identique/idnumbers/pull/377)).
- `parse()` returns `None` for IDs that are valid but have no complete birth date or no check digit to report: BEL
  numbers with an unknown month or day ([#373](https://github.com/identique/idnumbers/pull/373)), and CZE and SVK
  9-digit birth numbers ([#384](https://github.com/identique/idnumbers/pull/384)). `ParseResult` is unchanged. BEL
  numbers with `yy` 50 now parse to 1950, not 2050 ([#373](https://github.com/identique/idnumbers/pull/373)).
- Some types now accept or reject whole groups of IDs. The largest shifts are GEO (11 digits instead of 9,
  [#400](https://github.com/identique/idnumbers/pull/400)), ZWE (a new check letter,
  [#398](https://github.com/identique/idnumbers/pull/398)), CHL 7-digit RUTs
  ([#382](https://github.com/identique/idnumbers/pull/382)), CHE AHV numbers
  ([#377](https://github.com/identique/idnumbers/pull/377)) and TWN
  ([#396](https://github.com/identique/idnumbers/pull/396)). See "Validity changes".

### Validity changes

Each bullet says what is accepted now and what is rejected now. Vectors are taken from the pull requests, and most of
them are also tests.

- **BEL** national registration number ([#373](https://github.com/identique/idnumbers/pull/373)):
  - The post-2000 check digit was computed with an operator-precedence bug. Real numbers born from 2000, such as
    `01010100126`, were rejected, and any `yy` below 50 with check number `29` was accepted (`00010100129`, now
    rejected).
  - The century is inferred from the check digit, as the Rijksregister instruction IT000 requires. 1900-1949 numbers
    such as `47010100190` are now valid. A future 20xx birth year is rejected.
  - For `yy` 50, validity is unchanged, but `parse()` now returns 1950 instead of 2050 (`50010100156` was read as
    2050-01-01 and is now 1950-01-01).
  - A month `00` or a day `00` (an incomplete birth date, for example `85003003376`) is now valid and `parse()` returns
    `None`. A day that does not exist in its month, and a month above 12, stay invalid.
- **BEL** entity VAT ([#373](https://github.com/identique/idnumbers/pull/373)): a 10-digit number must start with `0` or
  `1`. A 9-digit number may start with any digit.
- **BGR** EGN ([#375](https://github.com/identique/idnumbers/pull/375)): a weighted-sum remainder of 10 gives check
  digit 0. About 1 in 11 real EGNs, such as `8507300050` and `0001011000`, were rejected before.
- **BGR** 13-digit EIK/BULSTAT ([#375](https://github.com/identique/idnumbers/pull/375)): the check now weights digits 9
  to 12, and the first nine digits must be a valid 9-digit EIK. `0114806291686` is valid and `0114806291688` is not.
  9-digit codes are unchanged.
- **CHE** AHV/AVS number ([#377](https://github.com/identique/idnumbers/pull/377)):
  - The check digit uses the EAN-13 weights 1 and 3. Genuine numbers such as `756.9217.0769.85` are now accepted and
    wrong ones such as `756.0000.5678.17` are rejected.
  - The dot in the pattern is escaped, so `756.1234.5678-97` is `False`.
- **CHE** UID (`BusinessID`) ([#377](https://github.com/identique/idnumbers/pull/377)): the modulus 11 check digit is
  verified. `CHE-116.281.710` is valid and `CHE-116.281.715` is not.
- **CHL** RUT ([#382](https://github.com/identique/idnumbers/pull/382),
  [#410](https://github.com/identique/idnumbers/pull/410)):
  - The weights run from the right, so 7-digit RUTs are checked correctly. `1.111.111-4` is valid, `1.111.111-3` is not.
    8-digit RUTs are unchanged.
  - A lowercase check character is accepted: `10.000.013-k` is valid.
- **CZE** and **SVK** birth number ([#384](https://github.com/identique/idnumbers/pull/384)):
  - Check digit 0 is accepted when the first nine digits leave remainder 10: `5401031230` is valid.
  - 9-digit numbers are accepted for births up to 1953. They need a valid date with `yy` 53 or below, for example
    `530101123`.
  - A 10-digit number with `yy` 00 to 53 is read as 2000 to 2053 and a birth date in the future is invalid. `5001010003`
    is no longer read as 1950. `METADATA.min_length` is now 9.
- **ITA** fiscal code ([#386](https://github.com/identique/idnumbers/pull/386)):
  - Omocodia codes are now valid. `RSSMRA8LM01H501W` used to make `validate()` raise.
  - `parse()` maps the letters back to digits (`area_code` is `H500` instead of `H50L`) and picks the century: 20yy
    unless that date is in the future, otherwise 19yy. `RSSMRA40M01H501B` is born in 1940. Validity does not change for
    IDs without omocodia letters.
- **KWT** civil number ([#388](https://github.com/identique/idnumbers/pull/388)): a number with a correct check digit
  but an impossible birth date (`200022900006`, `200013200008`, `200001000009`) used to raise. `validate()` is now
  `False` and `parse()` is `None`.
- **NOR** national ID ([#389](https://github.com/identique/idnumbers/pull/389)):
  - An impossible date (31 April, 30 February, day or month `00`, `00000000000`) gives `False` instead of raising.
  - D-numbers (day plus 40, for example `41019912351`) and H-numbers (month plus 40, for example `01419912340`) are now
    valid and `parse()` returns the real birth date. A number with both offsets, and FH-numbers, stay invalid.
- **ROU** personal numerical code ([#391](https://github.com/identique/idnumbers/pull/391)): the first digit 6 (women
  born 2000 to 2099) no longer raises, and `6050315121230` is valid. The first digit 2 now means 1900 to 1999 and 4
  means 1800 to 1899, so `4000229011237` (29 February 1800) is invalid.
- **SGP** NRIC/FIN ([#392](https://github.com/identique/idnumbers/pull/392)): M-series FINs add a start constant of 3 to
  the weighted sum. `M1234567K` and `M3960741N` are now valid, and `M1234567N` is not. The S, T, F and G series are
  unchanged.
- **ZAF** national ID ([#394](https://github.com/identique/idnumbers/pull/394),
  [#275](https://github.com/identique/idnumbers/pull/275)): non-numeric input such as `abc` raised `ValueError` and now
  gives `False`. IDs with month 10 are accepted too, see the CHN and ZAF month pattern entry below.
- **TWN** national ID ([#396](https://github.com/identique/idnumbers/pull/396)): a weighted sum that is a multiple of 10
  gives check digit 0. About 1 in 10 genuine IDs, such as `M162773050` and `A120229780`, were rejected before.
- **ZWE** national ID ([#398](https://github.com/identique/idnumbers/pull/398)): the check letter is the whole number
  modulo 23, as the cited source says, and not the digit sum. `502001148W50` and `082095850T42` are now valid.
  `751919620S86` is now invalid, and `751919620J86` is the valid one. About 22 in 23 of the IDs that passed the old
  digit-sum rule are now rejected.
- **GEO** personal number ([#400](https://github.com/identique/idnumbers/pull/400)): the number has 11 digits, and may
  start with 0. `01001011234` is valid. Every 9-digit string, which was valid before, is now invalid.
- **BRA** RG and **SWE** personal identity number ([#402](https://github.com/identique/idnumbers/pull/402),
  [#371](https://github.com/identique/idnumbers/pull/371)): a literal `|` is no longer part of the pattern
  (`12.345.678-|`, `811228|9874`). These inputs used to make `validate()` raise and now give `False`.
- **CHN** and **ZAF** month pattern ([#275](https://github.com/identique/idnumbers/pull/275)): the pattern accepted
  months 01 to 09, 11 and 12 but not 10. IDs with month 10, for example CHN `372925199510103222`, are now valid.
- **NZL** driver licence ([#369](https://github.com/identique/idnumbers/pull/369)): the two leading characters must be
  ASCII. `AB123456` is valid, and `ÄB123456` and `ΑΒ123456` (Greek capitals) are rejected.

### New ID types

- **Cyprus** tax identification number, `CYP.TaxNumber` (also `CYP.NationalID` and `CYP.TIN`)
  ([#261](https://github.com/identique/idnumbers/pull/261),
  [#265](https://github.com/identique/idnumbers/pull/265)).
- **Czech Republic** tax number, DIČ, `CZE.TaxNumber` (also `CZE.TIN`)
  ([#266](https://github.com/identique/idnumbers/pull/266)). It follows python-stdnum: 8-digit entity numbers must not
  start with 9, 9-digit numbers starting with 6 have a special check digit, and every other 9 or 10-digit number is
  validated as a birth number ([#384](https://github.com/identique/idnumbers/pull/384)).
- **Denmark** entity VAT, `DNK.EntityVAT`, also known as CVR or SE (also `DNK.TIN.entity`)
  ([#274](https://github.com/identique/idnumbers/pull/274)).

### Other fixes

- `parse()` no longer raises on malformed input: BGR returns `None` on a failed match, UKR checks the pattern before
  calling `int()`, and LKA (old) catches `OverflowError` in the date arithmetic
  ([#371](https://github.com/identique/idnumbers/pull/371)).
- GRC, ISR and LVA no longer index `id_number[-1]` for an empty string, and NZL NHI no longer has an empty alternative
  in its pattern ([#371](https://github.com/identique/idnumbers/pull/371)).
- `idnumbers.nationalid.util.match_regexp()` is new. `validate_regexp()` and every `parse()` that reads the pattern now
  use it, so they match the whole input ([#369](https://github.com/identique/idnumbers/pull/369)).

### Internal, docs and CI

- CI runs the tests on Python 3.9 to 3.14 with current GitHub Actions, and `setup.py` lists the 3.13 and 3.14
  classifiers ([#368](https://github.com/identique/idnumbers/pull/368)).
- A tool, `python3 -m tools.collect_regexp`, dumps the regular expressions of all ID types, and the aliases of MKD, MNE
  and SRB `JMBG`, PAK `CNIC`, SMR `SSI` and VEN `RIF` now use `alias_of`
  ([#269](https://github.com/identique/idnumbers/pull/269)).
- The API docs are now built with the reStructuredText docformat, and the `match_regexp` docstring renders correctly
  ([#380](https://github.com/identique/idnumbers/pull/380), [#408](https://github.com/identique/idnumbers/pull/408)).
- The README gains an "Input handling" section ([#371](https://github.com/identique/idnumbers/pull/371),
  [#403](https://github.com/identique/idnumbers/pull/403)). New tests sweep every ID type to check that `validate()`
  never raises and rejects a trailing newline and non-ASCII digits
  ([#369](https://github.com/identique/idnumbers/pull/369), [#371](https://github.com/identique/idnumbers/pull/371)).
- Test and docs tidy-ups with no behaviour change: [#403](https://github.com/identique/idnumbers/pull/403),
  [#405](https://github.com/identique/idnumbers/pull/405), [#406](https://github.com/identique/idnumbers/pull/406),
  [#407](https://github.com/identique/idnumbers/pull/407), [#411](https://github.com/identique/idnumbers/pull/411),
  [#412](https://github.com/identique/idnumbers/pull/412), [#413](https://github.com/identique/idnumbers/pull/413),
  [#414](https://github.com/identique/idnumbers/pull/414), [#416](https://github.com/identique/idnumbers/pull/416) and
  [#417](https://github.com/identique/idnumbers/pull/417) (misplaced method docstrings moved to the top of their
  functions, with a test that keeps them there).
