from unittest import TestCase

from idnumbers.nationalid import COL


class TestCOLNationalIDValidation(TestCase):
    def test_normal_case(self):
        self.assertTrue(COL.NUIP.validate('901.458.652-7'))
        self.assertTrue(COL.NUIP.validate('800.134.536-3'))
        self.assertTrue(COL.NUIP.validate('900701704-1'))
        self.assertTrue(COL.NUIP.validate('52.238.803-1'))

    def test_error_case(self):
        self.assertFalse(COL.NUIP.validate('901.458.652-6'))
        self.assertFalse(COL.NUIP.validate('800.134.536-2'))
