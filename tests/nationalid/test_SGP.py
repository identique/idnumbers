from unittest import TestCase, main

from idnumbers.nationalid import SGP


class TestSGPValidation(TestCase):
    def test_normal_case(self):
        self.assertTrue(SGP.NationalID.validate('S8076606H'))
        self.assertTrue(SGP.NationalID.validate('S1728872E'))
        self.assertTrue(SGP.NationalID.validate('G4549883U'))
        self.assertTrue(SGP.NationalID.validate('G4552218R'))
        self.assertTrue(SGP.NationalID.validate('S2111122H'))

    def test_error_case(self):
        self.assertFalse(SGP.NationalID.validate('S1179607H'))
        self.assertFalse(SGP.NationalID.validate('X1728872E'))

    def test_m_series(self):
        # vectors from issue #309; M1234567K is the FormSG isMFinSeriesValid test vector
        self.assertTrue(SGP.NationalID.validate('M1234567K'))
        self.assertTrue(SGP.NationalID.validate('M3960741N'))
        # N was the check letter of the old algorithm, which lacked the +3 start constant
        self.assertFalse(SGP.NationalID.validate('M1234567N'))


if __name__ == '__main__':
    main()
