from datetime import date
from unittest import TestCase, main
from unittest.mock import patch
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


def synthetic_number(encoded_date, serial='987', separator='-'):
    """Make synthetic test vectors with an independently calculated Luhn digit."""
    payload = encoded_date[-6:] + serial
    total = 0
    for index, character in enumerate(payload):
        value = int(character) * (2 if index % 2 == 0 else 1)
        total += value // 10 + value % 10
    return encoded_date + separator + serial + str((-total) % 10)


class TestSWEExtendedFormats(TestCase):
    def test_person_formats(self):
        for prefix in ('81', '1981'):
            for separator in ('', '-', '+'):
                number = prefix + '1218' + separator + '9876'
                with self.subTest(number=number):
                    self.assertTrue(SWE.PersonalIdentityNumber.validate(number))
                    self.assertEqual(6, SWE.PersonalIdentityNumber.checksum(number))
                    result = SWE.PersonalIdentityNumber.parse(number)
                    self.assertEqual({'gender', 'yyyymmdd', 'checksum'}, set(result))
                    self.assertEqual(Gender.MALE, result['gender'])
                    self.assertEqual('6', result['checksum'])
                    if prefix == '1981':
                        self.assertEqual(date(1981, 12, 18), result['yyyymmdd'])

    def test_coordination_formats(self):
        for prefix in ('81', '1981'):
            for separator in ('', '-', '+'):
                number = prefix + '1278' + separator + '9873'
                with self.subTest(number=number):
                    self.assertTrue(SWE.CoordinationNumber.validate(number))
                    self.assertEqual(3, SWE.CoordinationNumber.checksum(number))
                    result = SWE.CoordinationNumber.parse(number)
                    self.assertEqual({'gender', 'yyyymmdd', 'checksum'}, set(result))
                    self.assertEqual(Gender.MALE, result['gender'])
                    self.assertEqual('3', result['checksum'])
                    if prefix == '1981':
                        self.assertEqual(date(1981, 12, 18), result['yyyymmdd'])

    def test_official_coordination_example(self):
        # Skatteverket's public-sector coordination-number page gives this male example:
        # https://www.skatteverket.se/offentligaaktorer/folkbokforing/
        # samordningsnummerforoffentligaaktorer.4.46ae6b26141980f1e2d3643.html
        self.assertEqual({'gender': Gender.MALE, 'yyyymmdd': date(1970, 10, 3), 'checksum': '1'},
                         SWE.CoordinationNumber.parse('701063-2391'))

    def test_legacy_and_compact_century(self):
        with patch('idnumbers.nationalid.swe.personal_id.date', wraps=date) as clock:
            clock.today.return_value = date(2026, 10, 7)
            for validator, encoded_day in ((SWE.PersonalIdentityNumber, '18'),
                                           (SWE.CoordinationNumber, '78')):
                for yy, expected_year in (('81', 1981), ('26', 2026), ('27', 1927), ('00', 2000)):
                    for separator in ('-', '+', ''):
                        number = synthetic_number(yy + '12' + encoded_day, separator=separator)
                        year = expected_year - (100 if separator == '+' else 0)
                        self.assertEqual(date(year, 12, 18), validator.parse(number)['yyyymmdd'])

    def test_explicit_centuries_and_leap_dates(self):
        for validator, day in ((SWE.PersonalIdentityNumber, '29'), (SWE.CoordinationNumber, '89')):
            for separator in ('', '-', '+'):
                for century in ('19', '20', '21'):
                    number = synthetic_number(century + '0002' + day, separator=separator)
                    with self.subTest(number=number):
                        self.assertEqual(validator.checksum(number), validator.checksum(number[2:]))
                        self.assertEqual(century == '20', validator.validate(number))
                        if century == '20':
                            self.assertEqual(date(2000, 2, 29), validator.parse(number)['yyyymmdd'])
                        else:
                            self.assertIsNone(validator.parse(number))

    def test_coordination_day_range_and_calendar(self):
        for encoded, decoded in (('19810161', date(1981, 1, 1)), ('19810191', date(1981, 1, 31))):
            number = synthetic_number(encoded, serial='002')
            self.assertEqual({'gender': Gender.FEMALE, 'yyyymmdd': decoded, 'checksum': number[-1]},
                             SWE.CoordinationNumber.parse(number))
        for encoded in ('19810160', '19810192', '19810289', '19810290', '19810491', '19810061', '19811361'):
            number = synthetic_number(encoded)
            with self.subTest(number=number):
                self.assertFalse(SWE.CoordinationNumber.validate(number))
                self.assertIsNone(SWE.CoordinationNumber.parse(number))
        for encoded in ('19810160', '19810192'):
            self.assertIsNone(SWE.CoordinationNumber.checksum(synthetic_number(encoded)))

    def test_separate_types_and_encoded_checksum(self):
        self.assertEqual(6, SWE.PersonalIdentityNumber.checksum('19811218-9876'))
        self.assertEqual(3, SWE.CoordinationNumber.checksum('19811278-9873'))
        self.assertFalse(SWE.CoordinationNumber.validate('19811278-9876'))
        self.assertFalse(SWE.PersonalIdentityNumber.validate('811278-9873'))
        self.assertFalse(SWE.NationalID.validate('811278-9873'))
        self.assertIsNone(SWE.NationalID.parse('811278-9873'))
        self.assertFalse(SWE.CoordinationNumber.validate('811218-9876'))
        self.assertIsNone(SWE.CoordinationNumber.parse('811218-9876'))
        self.assertTrue(SWE.NationalID.validate('19811218-9876'))
        self.assertEqual(SWE.PersonalIdentityNumber.parse('19811218-9876'),
                         SWE.NationalID.parse('19811218-9876'))

    def test_checksum_remains_calculator(self):
        for validator, encoded in ((SWE.PersonalIdentityNumber, '810231'),
                                   (SWE.CoordinationNumber, '810291')):
            number = synthetic_number(encoded)
            self.assertEqual(int(number[-1]), validator.checksum(number))
            self.assertFalse(validator.validate(number))
            self.assertIsNone(validator.parse(number))
            wrong_digit = number[:-1] + str((int(number[-1]) + 1) % 10)
            self.assertEqual(int(number[-1]), validator.checksum(wrong_digit))
            self.assertFalse(validator.validate(wrong_digit))
            self.assertIsNone(validator.parse(wrong_digit))

    def test_malformed_inputs(self):
        for validator, valid in ((SWE.PersonalIdentityNumber, '811218-9876'),
                                 (SWE.CoordinationNumber, '811278-9873')):
            malformed = [None, True, False, 8112189876, [], {}, '', ' ' + valid, valid + ' ',
                         valid + '\n', valid + '\r\n', valid.replace('-', '|'),
                         valid.replace('-', '--'), valid.replace('-', '+-'), valid.replace('-', '_'),
                         valid.replace('-', ' '), valid[:5] + '-' + valid[5:], valid[1:], valid + '0',
                         ''.join(chr(ord(c) + 0xFEE0) if c.isdigit() else c for c in valid),
                         ''.join(chr(0x0660 + int(c)) if c.isdigit() else c for c in valid),
                         synthetic_number(valid[:6], serial='000')]
            for number in malformed:
                with self.subTest(validator=validator, number=number):
                    self.assertFalse(validator.validate(number))
                    self.assertIsNone(validator.parse(number))
                    self.assertIsNone(validator.checksum(number))

    def test_wrong_checksum_and_serial_boundaries(self):
        for validator, encoded in ((SWE.PersonalIdentityNumber, '19811218'),
                                   (SWE.CoordinationNumber, '19811278')):
            for serial in ('001', '002', '999'):
                number = synthetic_number(encoded, serial=serial)
                self.assertTrue(validator.validate(number))
                wrong_digit = number[:-1] + str((int(number[-1]) + 1) % 10)
                self.assertFalse(validator.validate(wrong_digit))
                self.assertIsNone(validator.parse(wrong_digit))
                self.assertEqual(int(number[-1]), validator.checksum(wrong_digit))

    def test_metadata(self):
        for validator in (SWE.PersonalIdentityNumber, SWE.CoordinationNumber):
            self.assertEqual('SE', validator.METADATA.iso3166_alpha2)
            self.assertEqual(10, validator.METADATA.min_length)
            self.assertEqual(12, validator.METADATA.max_length)
            self.assertTrue(validator.METADATA.parsable)
            self.assertTrue(validator.METADATA.checksum)
            self.assertIsNone(validator.METADATA.alias_of)


if __name__ == '__main__':
    main()
