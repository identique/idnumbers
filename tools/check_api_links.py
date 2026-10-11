"""Check exact regression hrefs in rendered pydoctor docstrings, without fetching URLs."""

import argparse
import sys
from html.parser import HTMLParser
from pathlib import Path
from typing import Optional, Sequence


# Keep these rendered targets aligned with tests/test_docstring_links.py. Methods render on their owner's page.
# Static fixtures deliberately avoid importing the library or depending on the renderer at check time.
WIKIPEDIA = 'https://en.wikipedia.org/wiki/'
EXPECTED_LINKS: tuple[tuple[str, str], ...] = (
    ('idnumbers.nationalid.pak.national_id.NationalID.html', WIKIPEDIA + 'CNIC_(Pakistan%29#Security_features'),
    ('idnumbers.nationalid.esp.dni.DNI.html', WIKIPEDIA + 'Documento_Nacional_de_Identidad_(Spain%29#Number'),
    ('idnumbers.nationalid.arg.national_id.NationalID.html',
     WIKIPEDIA + 'Documento_Nacional_de_Identidad_(Argentina%29'),
    ('idnumbers.nationalid.mys.nric.NRIC.html',
     WIKIPEDIA + 'Malaysian_identity_card#Structure_of_the_National_Registration_Identity_Card_Number_(NRIC%29'),
    ('idnumbers.nationalid.bgd.national_id.NationalID.html', WIKIPEDIA + 'National_identity_card_(Bangladesh%29'),
    ('idnumbers.nationalid.bgd.old_national_id.OldNationalID.html',
     WIKIPEDIA + 'National_identity_card_(Bangladesh%29'),
    ('idnumbers.nationalid.nor.national_id.NationalID.html', WIKIPEDIA + 'National_identity_number_(Norway%29'),
    ('idnumbers.nationalid.nor.national_id.NationalID.html',
     WIKIPEDIA + 'National_identity_number_(Norway%29#Check_digits'),
    ('idnumbers.nationalid.hrv.personal_id.PersonalID.html', WIKIPEDIA + 'Personal_identification_number_(Croatia%29'),
    ('idnumbers.nationalid.swe.personal_id.PersonalIdentityNumber.html',
     WIKIPEDIA + 'Personal_identity_number_(Sweden%29'),
    ('idnumbers.nationalid.swe.personal_id.PersonalIdentityNumber.html',
     WIKIPEDIA + 'Personal_identity_number_(Sweden%29#Checksum'),
    ('idnumbers.nationalid.nor.national_id.NationalID.html', 'https://no.wikipedia.org/wiki/F%C3%B8dselsnummer'),
)


class DocstringLinks(HTMLParser):
    """Collect anchors only inside pydoctor's class/module and method docstring divs."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.hrefs: set[str] = set()
        self._div_depth = 0
        self._docstring_depths: list[int] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, Optional[str]]]) -> None:
        attributes = dict(attrs)
        if tag == 'div':
            self._div_depth += 1
            classes = (attributes.get('class') or '').split()
            if 'moduleDocstring' in classes or 'docstring' in classes:
                self._docstring_depths.append(self._div_depth)
        if tag == 'a' and self._docstring_depths:
            href = attributes.get('href')
            if href is not None:
                self.hrefs.add(href)

    def handle_endtag(self, tag: str) -> None:
        if tag == 'div':
            if self._docstring_depths and self._docstring_depths[-1] == self._div_depth:
                self._docstring_depths.pop()
            self._div_depth = max(0, self._div_depth - 1)

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, Optional[str]]]) -> None:
        self.handle_starttag(tag, attrs)
        self.handle_endtag(tag)


def check_links(directory: Path) -> list[str]:
    """Return actionable missing-page/href errors for the fixed rendered regression corpus."""
    errors: list[str] = []
    pages = dict.fromkeys(page for page, _ in EXPECTED_LINKS)
    for page in pages:
        path = directory / page
        try:
            html = path.read_text(encoding='utf-8')
        except FileNotFoundError:
            errors.append(f'{path}: missing rendered page; build the API documentation first')
            continue
        except (OSError, UnicodeError) as exc:
            errors.append(f'{path}: cannot read rendered page: {exc}')
            continue
        parser = DocstringLinks()
        parser.feed(html)
        parser.close()
        for expected_page, href in EXPECTED_LINKS:
            if expected_page == page and href not in parser.hrefs:
                errors.append(f'{path}: missing docstring href {href!r}')
    return errors


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', type=Path, help='directory containing the rendered pydoctor HTML pages')
    args = parser.parse_args(argv)
    errors = check_links(args.directory)
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print(f'Checked {len(EXPECTED_LINKS)} rendered API docstring hrefs.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
