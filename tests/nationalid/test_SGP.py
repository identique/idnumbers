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


if __name__ == '__main__':
    main()
