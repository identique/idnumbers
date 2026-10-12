"""Build the coverage badge endpoint JSON that CI publishes to the ``badges`` branch.

The output follows the shields.io endpoint schema, so the README can render it with
``https://img.shields.io/endpoint?url=...``.

Usage::

    python -m coverage json -o coverage.json
    python -m tools.coverage_badge coverage.json coverage-badge/coverage.json
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, Mapping, Optional, Sequence


def badge_color(percent: float) -> str:
    """Return the shields.io colour name for a coverage percentage.

    :param percent: the coverage percentage, from 0 to 100.
    :return: ``brightgreen`` from 90, ``green`` from 80, ``yellowgreen`` from 70, ``yellow`` from 60, else ``red``.
    """
    if percent >= 90:
        return "brightgreen"
    if percent >= 80:
        return "green"
    if percent >= 70:
        return "yellowgreen"
    if percent >= 60:
        return "yellow"
    return "red"


def badge(report: Mapping[str, object]) -> Dict[str, object]:
    """Build the shields.io endpoint object from a ``coverage json`` report.

    The message shows ``totals.percent_covered_display`` verbatim, so it keeps the precision configured for
    ``coverage report``.

    :param report: the parsed ``coverage json`` output.
    :return: the endpoint object, with ``schemaVersion``, ``label``, ``message`` and ``color``.
    :raises ValueError: if ``totals`` or one of its two percentage fields is missing or has the wrong type.
    """
    totals = report.get("totals")
    if not isinstance(totals, dict):
        raise ValueError("the report has no 'totals' object")
    percent = totals.get("percent_covered")
    if isinstance(percent, bool) or not isinstance(percent, (int, float)):
        raise ValueError("'totals.percent_covered' is missing or not a number")
    display = totals.get("percent_covered_display")
    if not isinstance(display, str) or not display:
        raise ValueError("'totals.percent_covered_display' is missing or not a string")
    return {"schemaVersion": 1, "label": "coverage", "message": f"{display}%", "color": badge_color(percent)}


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Read a ``coverage json`` report and write the badge endpoint JSON.

    :param argv: the command-line arguments, ``sys.argv[1:]`` by default.
    :return: ``0`` on success, ``1`` after printing ``coverage_badge: <reason>`` to stderr on a failure.
    """
    parser = argparse.ArgumentParser(description="Build the coverage badge endpoint JSON from a coverage JSON report.")
    parser.add_argument("report", type=Path, help="the JSON written by 'python -m coverage json'")
    parser.add_argument("output", type=Path, help="where to write the shields.io endpoint JSON")
    args = parser.parse_args(argv)
    try:
        report = json.loads(args.report.read_text(encoding="utf-8"))
        if not isinstance(report, dict):
            raise ValueError("the report is not a JSON object")
        endpoint = badge(report)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(endpoint) + "\n", encoding="utf-8")
    except (OSError, ValueError) as error:  # json.JSONDecodeError is a ValueError
        print(f"coverage_badge: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
