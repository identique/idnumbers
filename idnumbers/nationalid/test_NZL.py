from unittest import TestCase, main
from idnumbers.nationalid import NZL


class TestNZLDriverLicenseNumberValidation(TestCase):
    def test_normal_case(self):
        self.assertTrue(NZL.DriverLicenseNumber.validate('AA345678'))
        self.assertTrue(NZL.DriverLicenseNumber.validate('aa123456'))

    def test_error_case(self):
        self.assertFalse(NZL.DriverLicenseNumber.validate('12-345-678'))
        self.assertFalse(NZL.DriverLicenseNumber.validate('AA000000'))
        self.assertFalse(NZL.DriverLicenseNumber.validate('B11111'))

    def test_with_metadata(self):
        self.assertIsNotNone(NZL.DriverLicenseNumber.METADATA)


class TestNZLPassportNumberValidation(TestCase):
    def test_normal_case(self):
        self.assertTrue(NZL.PassportNumber.validate('La615098'))
        self.assertTrue(NZL.PassportNumber.validate('LD615098'))
        self.assertTrue(NZL.PassportNumber.validate('lF615098'))
        self.assertTrue(NZL.PassportNumber.validate('n615098'))
        self.assertTrue(NZL.PassportNumber.validate('ea615098'))
        self.assertTrue(NZL.PassportNumber.validate('LH615098'))

    def test_error_case(self):
        self.assertFalse(NZL.PassportNumber.validate('12-345-678'))
        self.assertFalse(NZL.PassportNumber.validate('LH000000'))
        self.assertFalse(NZL.PassportNumber.validate('B11111'))

    def test_with_metadata(self):
        self.assertIsNotNone(NZL.DriverLicenseNumber.METADATA)


class TestNZLIRDValidation(TestCase):
    def test_normal_case(self):
        self.assertTrue(NZL.InlandRevenueDepartmentNumber.validate('49091850'))
        self.assertTrue(NZL.InlandRevenueDepartmentNumber.validate('35901981'))
        self.assertTrue(NZL.InlandRevenueDepartmentNumber.validate('136410132'))
        self.assertTrue(NZL.InlandRevenueDepartmentNumber.validate('49-091-850'))
        self.assertTrue(NZL.InlandRevenueDepartmentNumber.validate('35-901-981'))
        self.assertTrue(NZL.InlandRevenueDepartmentNumber.validate('136-410-132'))

    def test_error_case(self):
        self.assertFalse(NZL.InlandRevenueDepartmentNumber.validate('49091851'))
        self.assertFalse(NZL.InlandRevenueDepartmentNumber.validate('35901982'))
        self.assertFalse(NZL.InlandRevenueDepartmentNumber.validate('136410133'))
        self.assertFalse(NZL.InlandRevenueDepartmentNumber.validate('49 091 850'))
        self.assertFalse(NZL.InlandRevenueDepartmentNumber.validate('35.901.981'))
        self.assertFalse(NZL.InlandRevenueDepartmentNumber.validate('136/410/132'))

    def test_with_metadata(self):
        self.assertIsNotNone(NZL.InlandRevenueDepartmentNumber.METADATA)


class TestNZLNHIValidation(TestCase):
    def test_normal_case(self):
        self.assertTrue(NZL.NationalHealthIndexNumber.validate('ZZZ0016'))
        self.assertTrue(NZL.NationalHealthIndexNumber.validate('ZZZ0024'))
        self.assertTrue(NZL.NationalHealthIndexNumber.validate('ZZZ00AX'))
        self.assertTrue(NZL.NationalHealthIndexNumber.validate('ALU18KZ'))

    def test_error_case(self):
        self.assertFalse(NZL.NationalHealthIndexNumber.validate('ZZZ0017'))
        self.assertFalse(NZL.NationalHealthIndexNumber.validate('ZZZ00AZ'))
        self.assertFalse(NZL.NationalHealthIndexNumber.validate('ALU28KZ'))

    def test_with_metadata(self):
        self.assertIsNotNone(NZL.InlandRevenueDepartmentNumber.METADATA)


if __name__ == '__main__':
    main()
