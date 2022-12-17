from unittest import TestCase, main
from idnumbers.nationalid import AUS


class TestAUSTFNValidation(TestCase):
    def test_normal_case(self):
        self.assertTrue(AUS.TaxFileNumber.validate('123456782'))
        self.assertTrue(AUS.TaxFileNumber.validate('32547689'))

    def test_error_case(self):
        self.assertFalse(AUS.TaxFileNumber.validate('1234567'))
        self.assertFalse(AUS.TaxFileNumber.validate('12345678'))
        self.assertFalse(AUS.TaxFileNumber.validate('123456781'))

    def test_number_type(self):
        # if the user doesn't follow the type hinting, we still handle it
        self.assertTrue(AUS.TaxFileNumber.validate(123456782))

    def test_with_regex(self):
        self.assertRegex('123456782', AUS.TaxFileNumber.METADATA.regexp)

    def test_with_metadata(self):
        self.assertIsNotNone(AUS.TaxFileNumber.METADATA)


class TestAUSDriverLicenseNumberValidation(TestCase):
    def test_normal_case(self):
        self.assertTrue(AUS.DriverLicenseNumber.validate('12 345 678'))
        self.assertTrue(AUS.DriverLicenseNumber.validate('12345678'))
        self.assertTrue(AUS.DriverLicenseNumber.validate('123 456 789'))
        self.assertTrue(AUS.DriverLicenseNumber.validate('123456789'))
        self.assertTrue(AUS.DriverLicenseNumber.validate('A12345'))
        self.assertTrue(AUS.DriverLicenseNumber.validate('123-456-7890'))
        self.assertTrue(AUS.DriverLicenseNumber.validate('1234567890'))

    def test_error_case(self):
        self.assertFalse(AUS.DriverLicenseNumber.validate('12-345-678'))
        self.assertFalse(AUS.DriverLicenseNumber.validate('123 456 78'))
        self.assertFalse(AUS.DriverLicenseNumber.validate('0123456'))
        self.assertFalse(AUS.DriverLicenseNumber.validate('123 456 7890'))
        self.assertFalse(AUS.DriverLicenseNumber.validate('123-450-0000'))
        self.assertFalse(AUS.DriverLicenseNumber.validate('B11111'))

    def test_with_metadata(self):
        self.assertIsNotNone(AUS.DriverLicenseNumber.METADATA)


class TestAUSMedicareNumberValidation(TestCase):
    def test_normal_case(self):
        self.assertTrue(AUS.MedicareNumber.validate('2123 45670 1'))
        self.assertTrue(AUS.MedicareNumber.validate('2123 45670 2'))
        self.assertTrue(AUS.MedicareNumber.validate('2123456701'))
        self.assertTrue(AUS.MedicareNumber.validate('2428 77813 2-1'))
        self.assertTrue(AUS.MedicareNumber.validate('2428 77813 2-2'))
        self.assertTrue(AUS.MedicareNumber.validate('2428 77813 2-3'))
        self.assertTrue(AUS.MedicareNumber.validate('2428 77813 2/1'))

    def test_error_case(self):
        self.assertFalse(AUS.MedicareNumber.validate('2223 45670 1'))
        self.assertFalse(AUS.MedicareNumber.validate('2429 77813 2-1'))
        self.assertFalse(AUS.MedicareNumber.validate('0123456'))

    def test_with_metadata(self):
        self.assertIsNotNone(AUS.MedicareNumber.METADATA)


if __name__ == '__main__':
    main()
