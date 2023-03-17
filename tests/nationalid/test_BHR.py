from unittest import TestCase

from idnumbers.nationalid import BHR


class TestBHRValidation(TestCase):
    def test_normal_case(self):
        self.assertTrue(BHR.NationalID.validate('051108109'))

    def test_error_case(self):
        self.assertFalse(BHR.NationalID.validate('053108109'))

    def test_parse(self):
        result = BHR.NationalID.parse('051108109')
        self.assertEqual('0511', result['yymm'])
        self.assertEqual('0810', result['sn'])
        self.assertEqual(9, result['checksum'])
