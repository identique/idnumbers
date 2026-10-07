# Changelog

Releases before 1.12.0 are listed on the [GitHub releases page](https://github.com/identique/idnumbers/releases).

## Unreleased

### Validity changes

- **ARG** DNI ([#280](https://github.com/identique/idnumbers/issues/280)): 7-digit numbers (below 10 million), such as
  `5.123.456` and `5123456`, are now accepted. `METADATA.min_length` is 7.
- **BRA** CPF ([#284](https://github.com/identique/idnumbers/issues/284)): numbers made of one repeated digit,
  `000.000.000-00` to `999.999.999-99`, are now rejected. They pass the check digits, but the federal civil-registry
  system SIRC lists repeated digits as a reason for an invalid CPF. `checksum()` is unchanged.

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
