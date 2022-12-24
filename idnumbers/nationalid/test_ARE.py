from unittest import TestCase, main

from idnumbers.nationalid import ARE


class TestUAEValidation(TestCase):
    def test_normal_case(self):
        self.assertTrue(ARE.EmiratesIDNumber.validate('784-1980-1234567-8'))
        self.assertTrue(ARE.EmiratesIDNumber.validate('784198012345678'))
        self.assertTrue(ARE.EmiratesIDNumber.validate('784-1979-1234567-1'))
        self.assertTrue(ARE.EmiratesIDNumber.validate('784-1952-0464048-6'))
        self.assertTrue(ARE.EmiratesIDNumber.validate('784-1968-6570305-0'))

    def test_error_case(self):
        self.assertFalse(ARE.EmiratesIDNumber.validate('784-1981-1234567-9'))
        self.assertFalse(ARE.EmiratesIDNumber.validate('784198212345679'))
        self.assertFalse(ARE.EmiratesIDNumber.validate('784-199234567-1'))
        self.assertFalse(ARE.EmiratesIDNumber.validate('784-2002-12345'))

    def test_parse(self):
        result = ARE.EmiratesIDNumber.parse('784-1968-6570305-0')
        self.assertEqual(1968, result['yyyy'])
        self.assertEqual('6570305', result['sn'])
        self.assertEqual(0, result['checksum'])


if __name__ == '__main__':
    main()
