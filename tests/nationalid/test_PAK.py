from unittest import TestCase

from idnumbers.nationalid import PAK
from idnumbers.nationalid.constant import Gender


class TestPAKValidation(TestCase):
    def test_normal_case(self):
        self.assertTrue(PAK.NationalID.validate('57469-0532456-7'))
        self.assertTrue(PAK.NationalID.validate('0975345678053'))
        self.assertTrue(PAK.NationalID.validate('0975431479567'))
        self.assertTrue(PAK.NationalID.validate('73654-8723402-3'))
        self.assertTrue(PAK.NationalID.validate('2374982638947'))
        self.assertTrue(PAK.NationalID.validate('26349-6293643-8'))

    def test_error_case(self):
        self.assertFalse(PAK.NationalID.validate('57469-0532456'))

    def test_parse(self):
        result = PAK.NationalID.parse('57469-0532456-7')
        self.assertEqual('57469', result['location'])
        self.assertEqual(Gender.MALE, result['gender'])
        self.assertEqual('0532456', result['sn'])
