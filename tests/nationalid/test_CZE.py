from unittest import TestCase

from idnumbers.nationalid.CZE import TIN


# only test TIN because national id is shared with others
class TestCZETaxNumberValidation(TestCase):
    def test_normal_case(self):
        self.assertTrue(TIN.individual.validate('7103192745'))
        self.assertTrue(TIN.individual.validate('6956220612'))
        self.assertTrue(TIN.individual.validate('654123789'))
        self.assertTrue(TIN.individual.validate('682127228'))
        self.assertTrue(TIN.individual.validate('48207926'))
        self.assertTrue(TIN.individual.validate('69663963'))
        self.assertTrue(TIN.individual.validate('25938002'))

    def test_error_case(self):
        self.assertFalse(TIN.individual.validate('71031'))
        self.assertFalse(TIN.individual.validate('682127229'))
        self.assertFalse(TIN.individual.validate('48207927'))
