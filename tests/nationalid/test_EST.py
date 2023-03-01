from unittest import TestCase

from idnumbers.nationalid import EST
from idnumbers.nationalid.constant import Gender


class TestESTValidation(TestCase):
    def test_normal_case(self):
        self.assertTrue(EST.PersonalID.validate('37605030299'))

    def test_error_case(self):
        self.assertFalse(EST.PersonalID.validate('37605030290'))

    def test_parse(self):
        result = EST.PersonalID.parse('37605030299')
        self.assertEqual(1976, result['yyyymmdd'].year)
        self.assertEqual(5, result['yyyymmdd'].month)
        self.assertEqual(3, result['yyyymmdd'].day)
        self.assertEqual('029', result['sn'])
        self.assertEqual(Gender.MALE, result['gender'])
        self.assertEqual(9, result['checksum'])
