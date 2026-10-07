"""Informational micro-benchmarks for ``validate()``.

Run ``python bench/run.py`` from anywhere: the script imports the checkout it lives in, not an installed ``idnumbers``.
It times ``validate()`` on one known-valid vector for each of 10 ID types and prints a Markdown table of microseconds
per call (the best of ``--repeat`` repetitions).

The timings are informational only: they depend on the machine and are never compared against a threshold. The script
fails only when it crashes or when a vector no longer validates, which would make the timing meaningless.

This directory has no ``__init__.py`` and is not part of the published package.
"""

import argparse
import sys
import timeit
from pathlib import Path
from typing import Callable, List, NamedTuple, Optional, Sequence

# Import this checkout rather than a pip-installed copy (sys.path[0] is this directory otherwise).
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from idnumbers.nationalid import AUS, BRA, CHN, DEU, FRA, ITA, KOR, SVN, TWN, ZAF  # noqa: E402

DEFAULT_NUMBER = 5000
DEFAULT_REPEAT = 5


class Case(NamedTuple):
    country: str
    cls: str
    validate: Callable[[str], bool]
    vector: str


# One known-valid vector per ID type, each taken from the unit tests named in the comment.
CASES: List[Case] = [
    Case("CHN", "ResidentID", CHN.ResidentID.validate, "11010219840406970X"),  # tests/nationalid/test_CHN.py
    Case("TWN", "NationalID", TWN.NationalID.validate, "A123456789"),  # tests/nationalid/test_TWN.py
    Case("ZAF", "NationalID", ZAF.NationalID.validate, "7605300675088"),  # tests/nationalid/test_ZAF.py
    Case("AUS", "TaxFileNumber", AUS.TaxFileNumber.validate, "123456782"),  # tests/nationalid/test_AUS.py
    Case("BRA", "CPFNumber", BRA.CPFNumber.validate, "111.333.666-86"),  # tests/nationalid/test_BRA.py
    Case("DEU", "TaxID", DEU.TaxID.validate, "65929970489"),  # tests/nationalid/test_DEU.py
    Case("FRA", "INSEE", FRA.INSEE.validate, "255081416802538"),  # tests/nationalid/test_FRA.py
    Case("ITA", "FiscalCode", ITA.FiscalCode.validate, "MRTMTT91D08F205J"),  # tests/nationalid/test_ITA.py
    Case("KOR", "ResidentRegistration", KOR.ResidentRegistration.validate, "820701-2409184"),  # test_KOR.py
    Case("SVN", "UniqueMasterCitizenNumber", SVN.UniqueMasterCitizenNumber.validate, "0101006500006"),  # test_SVN.py
]


def positive_int(text: str) -> int:
    value = int(text)
    if value < 1:
        raise argparse.ArgumentTypeError("must be at least 1")
    return value


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Informational benchmarks for validate().")
    parser.add_argument("--number", type=positive_int, default=DEFAULT_NUMBER, help="calls per repetition")
    parser.add_argument("--repeat", type=positive_int, default=DEFAULT_REPEAT, help="repetitions (the best is kept)")
    args = parser.parse_args(argv)

    invalid = [f"{c.country}.{c.cls}({c.vector!r})" for c in CASES if c.validate(c.vector) is not True]
    if invalid:
        print("benchmark vectors that do not validate: " + ", ".join(invalid), file=sys.stderr)
        return 1

    print(f"validate(), best of {args.repeat} x {args.number} calls, Python {sys.version.split()[0]}")
    print()
    print("| Country | Class | µs per call |")
    print("| --- | --- | ---: |")
    for case in CASES:
        timer = timeit.Timer(lambda: case.validate(case.vector))
        best = min(timer.repeat(repeat=args.repeat, number=args.number))
        print(f"| {case.country} | {case.cls} | {best / args.number * 1e6:.2f} |")
    return 0


if __name__ == "__main__":
    sys.exit(main())
