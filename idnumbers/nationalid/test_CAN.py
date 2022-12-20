from unittest import TestCase, main

from idnumbers.nationalid import CAN


class TestBRASINValidation(TestCase):
    def test_normal_case(self):
        self.assertTrue(CAN.SocialInsuranceNumber.validate('130692544'))

    def test_error_case(self):
        self.assertFalse(CAN.SocialInsuranceNumber.validate('130692545'))

    def test_with_metadata(self):
        self.assertIsNotNone(CAN.SocialInsuranceNumber.METADATA)
        self.assertFalse(CAN.SocialInsuranceNumber.METADATA.parsable)
        self.assertTrue(CAN.SocialInsuranceNumber.METADATA.checksum)


if __name__ == '__main__':
    main()
