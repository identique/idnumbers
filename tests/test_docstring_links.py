"""Regression coverage for complete reStructuredText API-documentation URLs."""

import unittest

from idnumbers.nationalid.arg.national_id import NationalID as ArgentinaID
from idnumbers.nationalid.bgd.national_id import NationalID as BangladeshID
from idnumbers.nationalid.bgd.old_national_id import OldNationalID
from idnumbers.nationalid.esp.dni import DNI
from idnumbers.nationalid.hrv.personal_id import PersonalID
from idnumbers.nationalid.mys.nric import NRIC
from idnumbers.nationalid.nor.national_id import NationalID as NorwayID
from idnumbers.nationalid.pak.national_id import NationalID as PakistanID
from idnumbers.nationalid.swe.personal_id import PersonalIdentityNumber


class TestDocstringLinks(unittest.TestCase):
    def test_complete_escaped_uris(self):
        """Closing parentheses must not terminate automatic reST hyperlinks."""
        links = (
            (PakistanID, 'CNIC_(Pakistan%29#Security_features'),
            (DNI.checksum, 'Documento_Nacional_de_Identidad_(Spain%29#Number'),
            (ArgentinaID, 'Documento_Nacional_de_Identidad_(Argentina%29'),
            (NRIC, 'Malaysian_identity_card#Structure_of_the_National_Registration_Identity_Card_Number_(NRIC%29'),
            (BangladeshID, 'National_identity_card_(Bangladesh%29'),
            (OldNationalID, 'National_identity_card_(Bangladesh%29'),
            (NorwayID, 'National_identity_number_(Norway%29'),
            (NorwayID.checksum, 'National_identity_number_(Norway%29#Check_digits'),
            (PersonalID, 'Personal_identification_number_(Croatia%29'),
            (PersonalIdentityNumber, 'Personal_identity_number_(Sweden%29'),
            (PersonalIdentityNumber.checksum, 'Personal_identity_number_(Sweden%29#Checksum'),
        )
        for obj, path in links:
            with self.subTest(module=obj.__module__, object=obj.__qualname__):
                uri = 'https://en.wikipedia.org/wiki/' + path
                self.assertIsNotNone(obj.__doc__)
                docstring = obj.__doc__
                if obj is NRIC:
                    # reST joins whitespace in explicit hyperlink target continuations.
                    self.assertIn(".. _NRIC structure:", docstring)
                    target = docstring.split(".. _NRIC structure:", 1)[1]
                    docstring = "".join(target.split())
                self.assertIn(uri, docstring)
                self.assertNotIn(uri.replace('%29', ')'), docstring)

    def test_norway_prose_punctuation_is_not_part_of_uri(self):
        """The parenthesis surrounding a prose URL is not an escaped URI character."""
        self.assertIn('(https://no.wikipedia.org/wiki/F%C3%B8dselsnummer).', NorwayID.__doc__)
        self.assertNotIn('F%C3%B8dselsnummer%29', NorwayID.__doc__)


if __name__ == '__main__':
    unittest.main()
