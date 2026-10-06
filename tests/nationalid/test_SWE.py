from unittest import TestCase, main
from idnumbers.nationalid.constant import Gender

from idnumbers.nationalid import SWE
from idnumbers.nationalid.util import match_regexp


class TestSWEValidation(TestCase):
    def test_normal_case(self):
        self.assertTrue(SWE.PersonalIdentityNumber.validate('850709-9805'))
        self.assertTrue(SWE.PersonalIdentityNumber.validate('191231+2392'))

    def test_error_case(self):
        self.assertFalse(SWE.PersonalIdentityNumber.validate('850709-9802'))
        self.assertFalse(SWE.PersonalIdentityNumber.validate('191231+2391'))
        self.assertFalse(SWE.PersonalIdentityNumber.validate('850709_9805'))
        self.assertFalse(SWE.PersonalIdentityNumber.validate('850709 _ 9805'))

    def test_regexp_rejects_pipe_as_separator(self):
        # the separator class must not contain a literal '|' (#370); it is the regexp that has to
        # reject it, not just the checksum guard
        regexp = SWE.PersonalIdentityNumber.METADATA.regexp
        self.assertIsNone(match_regexp('811228|9874', regexp))
        self.assertFalse(SWE.PersonalIdentityNumber.validate('811228|9874'))
        self.assertIsNotNone(match_regexp('850709-9805', regexp))
        self.assertIsNotNone(match_regexp('191231+2392', regexp))
        self.assertTrue(SWE.PersonalIdentityNumber.validate('850709-9805'))

    def test_parse(self):
        result = SWE.PersonalIdentityNumber.parse('850709-9805')
        self.assertEqual(1985, result['yyyymmdd'].year)
        self.assertEqual(7, result['yyyymmdd'].month)
        self.assertEqual(9, result['yyyymmdd'].day)
        self.assertEqual(Gender.FEMALE, result['gender'])
        self.assertEqual('5', result['checksum'])


if __name__ == '__main__':
    main()
