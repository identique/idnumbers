"""Hermetic rendered API href regressions; no pydoctor installation or network needed."""

import html
import subprocess
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from idnumbers.api import ParseSuccess, ValidationResult
from tools.check_api_links import EXPECTED_LINKS, DocstringLinks, check_links


class TestApiDocstrings(unittest.TestCase):
    def test_builtin_exception_names_use_literal_markup(self):
        for result_type in (ValidationResult, ParseSuccess):
            with self.subTest(result_type=result_type.__name__):
                docstring = result_type.__doc__ or ""
                self.assertIn("``TypeError``", docstring)
                self.assertNotIn(":class:`TypeError`", docstring)


class TestApiLinks(unittest.TestCase):
    def setUp(self):
        self.temporary = TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)
        for page in dict.fromkeys(page for page, _ in EXPECTED_LINKS):
            anchors = "".join(
                f'<a href="{html.escape(href, quote=True)}">reference</a>'
                for expected_page, href in EXPECTED_LINKS
                if expected_page == page
            )
            (self.directory / page).write_text(
                f'<div class="moduleDocstring"><div><p>{anchors}</p></div></div>',
                encoding="utf-8",
            )

    def replace_href(self, index, replacement):
        page, href = EXPECTED_LINKS[index]
        path = self.directory / page
        content = path.read_text(encoding="utf-8")
        path.write_text(content.replace(html.escape(href, quote=True), replacement), encoding="utf-8")
        return path, href

    def test_complete_rendered_links(self):
        self.assertEqual(len(EXPECTED_LINKS), 12)
        self.assertEqual(check_links(self.directory), [])

    def test_method_docstring_and_html_entities(self):
        parser = DocstringLinks()
        parser.feed(
            '<div class="docstring functionBody"><div><a href="https://example.org/?a=1&amp;b=2">'
            "reference</a></div></div>"
        )
        self.assertEqual(parser.hrefs, {"https://example.org/?a=1&b=2"})

    def test_truncated_path_or_fragment(self):
        for index, bad_href in (
            (0, EXPECTED_LINKS[0][1].split("%29")[0]),
            (1, EXPECTED_LINKS[1][1].split("#")[0]),
            (2, EXPECTED_LINKS[2][1].replace("%29", ")")),
        ):
            with self.subTest(index=index):
                path, href = self.replace_href(index, bad_href)
                self.assertIn(f"{path}: missing docstring href {href!r}", check_links(self.directory))

    def test_explicit_target_continuation_must_render_as_one_uri(self):
        page, href = EXPECTED_LINKS[3]
        for bad_href in (href.split("#")[0], href.replace("#Structure", "#\n Structure")):
            with self.subTest(href=bad_href):
                (self.directory / page).write_text(
                    f'<div class="moduleDocstring"><a href="{bad_href}">NRIC structure</a></div>',
                    encoding="utf-8",
                )
                self.assertIn(f"{self.directory / page}: missing docstring href {href!r}", check_links(self.directory))

    def test_bare_visible_url_is_not_an_anchor(self):
        page, href = EXPECTED_LINKS[0]
        (self.directory / page).write_text(f'<div class="moduleDocstring">{href}</div>', encoding="utf-8")
        self.assertIn(f"{self.directory / page}: missing docstring href {href!r}", check_links(self.directory))

    def test_links_outside_docstring_containers_do_not_count(self):
        parser = DocstringLinks()
        anchor = '<a href="https://example.org/">reference</a>'
        parser.feed(
            f'<nav>{anchor}</nav><table class="summary">{anchor}</table>'
            f'<div class="moduleDocstring"><div class="docstring"><div>text</div></div></div>'
            f'{anchor}<div class="notdocstring">{anchor}</div><div class="docstring"/>{anchor}'
        )
        self.assertEqual(parser.hrefs, set())
        page, href = EXPECTED_LINKS[0]
        (self.directory / page).write_text(f'<table><a href="{href}">reference</a></table>', encoding="utf-8")
        self.assertIn(f"{self.directory / page}: missing docstring href {href!r}", check_links(self.directory))

    def test_norway_prose_punctuation_is_excluded(self):
        path, href = self.replace_href(11, EXPECTED_LINKS[11][1] + ").")
        self.assertIn(f"{path}: missing docstring href {href!r}", check_links(self.directory))

    def test_missing_page(self):
        path = self.directory / EXPECTED_LINKS[0][0]
        path.unlink()
        self.assertEqual(
            check_links(self.directory),
            [f"{path}: missing rendered page; build the API documentation first"],
        )

    def test_unreadable_page(self):
        path = self.directory / EXPECTED_LINKS[0][0]
        path.write_bytes(b"\xff")
        errors = check_links(self.directory)
        self.assertEqual(len(errors), 1)
        self.assertIn(f"{path}: cannot read rendered page:", errors[0])

    def run_cli(self):
        tool = Path(__file__).resolve().parents[1] / "tools" / "check_api_links.py"
        return subprocess.run(
            [sys.executable, str(tool), str(self.directory)],
            capture_output=True,
            text=True,
            check=False,
        )

    def test_cli_success(self):
        result = self.run_cli()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "Checked 12 rendered API docstring hrefs.\n")
        self.assertEqual(result.stderr, "")

    def test_cli_failure(self):
        path, href = self.replace_href(0, "https://example.org/broken")
        result = self.run_cli()
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, "")
        self.assertIn(f"{path}: missing docstring href {href!r}", result.stderr)


if __name__ == "__main__":
    unittest.main()
