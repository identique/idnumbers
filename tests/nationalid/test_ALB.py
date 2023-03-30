from unittest import TestCase

from idnumbers.nationalid import ALB


class TestALBValidation(TestCase):
    def test_normal_case(self):
        self.assertTrue(ALB.NationalID.validate('I90308094A'))

    def test_error_case(self):
        self.assertFalse(ALB.NationalID.validate('Z90308094Z'))

    def test_parse(self):
        result = ALB.NationalID.parse('I90308094A')
        self.assertEqual(1989, result['yyyymmdd'].year)
        self.assertEqual(3, result['yyyymmdd'].month)
        self.assertEqual(8, result['yyyymmdd'].day)
        self.assertEqual('094', result['sn'])
        self.assertEqual('A', result['checksum'])

    def test_alias(self):
        self.assertIsNone(ALB.IdentityNumber.METADATA.alias_of)
        self.assertEqual(ALB.IdentityNumber, ALB.NationalID.METADATA.alias_of)
