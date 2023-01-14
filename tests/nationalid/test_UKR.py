from unittest import TestCase, main
from idnumbers.nationalid import UKR
from idnumbers.nationalid.constant import Gender


class TestUKRTINValidation(TestCase):
    def test_normal_case(self):
        self.assertTrue(UKR.TaxpayerIDNumber.validate('3184710691'))
        self.assertTrue(UKR.TaxpayerIDNumber.validate('3289360690'))

    def test_error_case(self):
        self.assertFalse(UKR.TaxpayerIDNumber.validate('2019503024'))
        self.assertFalse(UKR.TaxpayerIDNumber.validate('019015514'))

    def test_parse(self):
        result = UKR.TaxpayerIDNumber.parse('3184710691')
        self.assertEqual(1987, result['yyyymmdd'].year)
        self.assertEqual(3, result['yyyymmdd'].month)
        self.assertEqual(12, result['yyyymmdd'].day)
        self.assertEqual(Gender.MALE, result['gender'])
        self.assertEqual(1, result['checksum'])

    def test_with_metadata(self):
        self.assertIsNotNone(UKR.TaxpayerIDNumber.METADATA)
        self.assertTrue(UKR.TaxpayerIDNumber.METADATA.parsable)
        self.assertTrue(UKR.TaxpayerIDNumber.METADATA.checksum)


class TestUKREINValidation(TestCase):
    def test_normal_case(self):
        self.assertTrue(UKR.EntityIDNumber.validate('32813827'))

    def test_error_case(self):
        self.assertFalse(UKR.EntityIDNumber.validate('21388124'))
        self.assertFalse(UKR.EntityIDNumber.validate('019015514'))

    def test_with_metadata(self):
        self.assertIsNotNone(UKR.EntityIDNumber.METADATA)
        self.assertFalse(UKR.EntityIDNumber.METADATA.parsable)
        self.assertTrue(UKR.EntityIDNumber.METADATA.checksum)


if __name__ == '__main__':
    main()
