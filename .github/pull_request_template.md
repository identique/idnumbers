## Issue

Closes #<!-- issue number; use Part of # for partial work -->

## Summary

<!-- Explain behavior, scope, compatibility, and trade-offs. -->

## Sources and vectors

<!-- Link authoritative sources for validity changes, and distinguish synthetic/public test vectors. -->

## Checks

- [ ] Issue-linked branch and title (`Fix #N - ...`), focused diff
- [ ] Valid/invalid, boundary, checksum/date and malformed-input tests as applicable
- [ ] Authoritative source cited; port used only as a reference
- [ ] Full unittest suite passes; Python 3.9 syntax/API compatibility preserved
- [ ] Strict mypy (including tools and documentation examples), ruff and coverage ≥97% pass
- [ ] README/documentation examples execute and strict-typecheck; generated guides regenerated and `--check` passes
- [ ] Shared-country parity checked; changed vectors noted on the port issue and pin/allowlist refresh coordinated
- [ ] Metadata example/masks, public re-exports and registry checked for new ID types
- [ ] CHANGELOG entry added; no manual VERSION edit or unapproved release
