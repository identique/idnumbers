"""Tests for tools/coverage_badge.py, which builds the README coverage badge endpoint JSON."""

import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from typing import Dict

from tools import coverage_badge


def report(percent: object, display: object) -> Dict[str, object]:
    return {"totals": {"percent_covered": percent, "percent_covered_display": display}}


class BadgeColorTest(unittest.TestCase):
    def test_thresholds(self) -> None:
        for percent, color in (
            (100, "brightgreen"),
            (90, "brightgreen"),
            (89.99, "green"),
            (80, "green"),
            (79.99, "yellowgreen"),
            (70, "yellowgreen"),
            (69.99, "yellow"),
            (60, "yellow"),
            (59.99, "red"),
            (0, "red"),
        ):
            with self.subTest(percent=percent):
                self.assertEqual(coverage_badge.badge_color(percent), color)


class BadgeTest(unittest.TestCase):
    def test_endpoint_uses_the_display_string_verbatim(self) -> None:
        self.assertEqual(
            coverage_badge.badge(report(97.3612, "97.36")),
            {"schemaVersion": 1, "label": "coverage", "message": "97.36%", "color": "brightgreen"},
        )

    def test_color_follows_the_number_not_the_display_string(self) -> None:
        self.assertEqual(coverage_badge.badge(report(59.9, "60"))["color"], "red")

    def test_invalid_reports_raise_value_error(self) -> None:
        for name, bad in (
            ("no totals", {}),
            ("totals not an object", {"totals": []}),
            ("no percent", {"totals": {"percent_covered_display": "97.36"}}),
            ("no display", {"totals": {"percent_covered": 97.36}}),
            ("string percent", report("97.36", "97.36")),
            ("bool percent", report(True, "1")),
            ("non-string display", report(97.36, 97.36)),
            ("empty display", report(97.36, "")),
        ):
            with self.subTest(name):
                with self.assertRaises(ValueError):
                    coverage_badge.badge(bad)


class MainTest(unittest.TestCase):
    def test_round_trip_writes_the_endpoint_json(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "coverage.json"
            source.write_text(json.dumps(report(97.3612, "97.36")), encoding="utf-8")
            output = Path(directory) / "nested" / "coverage.json"
            self.assertEqual(coverage_badge.main([str(source), str(output)]), 0)
            self.assertEqual(
                output.read_text(encoding="utf-8"),
                '{"schemaVersion": 1, "label": "coverage", "message": "97.36%", "color": "brightgreen"}\n',
            )

    def test_missing_input_fails_with_a_message(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "out" / "coverage.json"
            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                code = coverage_badge.main([str(Path(directory) / "missing.json"), str(output)])
            self.assertEqual(code, 1)
            self.assertTrue(stderr.getvalue().startswith("coverage_badge: "))
            self.assertFalse(output.exists())

    def test_invalid_json_and_invalid_report_fail_with_a_message(self) -> None:
        for name, text in (("invalid JSON", "{not json"), ("not an object", "[]"), ("no totals", "{}")):
            with self.subTest(name), tempfile.TemporaryDirectory() as directory:
                source = Path(directory) / "coverage.json"
                source.write_text(text, encoding="utf-8")
                output = Path(directory) / "coverage-badge.json"
                stderr = io.StringIO()
                with contextlib.redirect_stderr(stderr):
                    code = coverage_badge.main([str(source), str(output)])
                self.assertEqual(code, 1)
                self.assertTrue(stderr.getvalue().startswith("coverage_badge: "))
                self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
