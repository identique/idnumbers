from datetime import date
from unittest import TestCase

import idnumbers
from idnumbers import FailureReason
from idnumbers.nationalid import EGY

# Every vector below is synthetic (built from the CYYMMDDGGSSSSV layout); none is a real person's number.


class TestEGYValidation(TestCase):
    def test_country_metadata(self):
        self.assertEqual(EGY.NationalID.METADATA.iso3166_alpha2, 'EG')
        self.assertEqual(EGY.NationalID.METADATA.country_name, 'Egypt')
        self.assertFalse(EGY.NationalID.METADATA.checksum)
        self.assertIsNone(EGY.NationalID.METADATA.checksum_algorithm)
        self.assertTrue(EGY.NationalID.validate(EGY.NationalID.METADATA.example))
        self.assertFalse(hasattr(EGY.NationalID, 'checksum'))

    def test_normal_case(self):
        for id_number in (
            '29001010100017',  # the metadata example
            '30002290100011',  # 29 February 2000, a leap year
            '29912310123456',  # 31 December 1999
            '30001018801239',  # governorate 88
            # governorate 99 is accepted: the governorate table is not official, so there is no allow-list
            '29001019901238',
            '29001010000017',  # governorate 00 is accepted for the same reason
            # the final digit is not verified: no check-digit algorithm is published
            '29001010100010',
            '29001010100019',
        ):
            with self.subTest(id_number=id_number):
                self.assertTrue(EGY.NationalID.validate(id_number))

    def test_error_case(self):
        for id_number in (
            '2900101010123',  # 13 digits
            '290010101001234',  # 15 digits
            '29011310100017',  # month 13
            '29000010100017',  # month 00
            '29001000100017',  # day 00
            '29001320100017',  # day 32
            '29002300100017',  # 30 February
            '30102290100011',  # 29 February 2001, not a leap year
            '29002290100017',  # 29 February 1900, not a leap year
            '19001010100017',  # century 1
            '49001010100017',  # century 4
            '09001010100017',  # century 0
            '2900101-0100017',
            '29001010100017\n',  # trailing newline
            ' 29001010100017',  # leading space
            '29001010100017 ',
            '２９００１０１０１０００１７',  # full-width digits
            '2900101010001A',
            '',
        ):
            with self.subTest(id_number=id_number):
                self.assertFalse(EGY.NationalID.validate(id_number))
                self.assertIsNone(EGY.NationalID.parse(id_number))

    def test_non_string_input(self):
        for value in (None, 29001010100017):
            with self.subTest(value=value):
                self.assertFalse(EGY.NationalID.validate(value))  # type: ignore[arg-type]
                self.assertIsNone(EGY.NationalID.parse(value))  # type: ignore[arg-type]

    def test_parse(self):
        self.assertEqual({'yyyymmdd': date(1990, 1, 1), 'governorate': '01', 'sn': '0001', 'check_digit': '7'},
                         EGY.NationalID.parse('29001010100017'))
        parsed = EGY.NationalID.parse('30002290100011')
        assert parsed is not None
        self.assertEqual(date(2000, 2, 29), parsed['yyyymmdd'])
        parsed = EGY.NationalID.parse('29912319901239')
        assert parsed is not None
        self.assertEqual(date(1999, 12, 31), parsed['yyyymmdd'])
        self.assertEqual('99', parsed['governorate'])
        self.assertEqual('0123', parsed['sn'])
        self.assertEqual('9', parsed['check_digit'])

    def test_unified_api(self):
        self.assertTrue(idnumbers.validate('EGY', '29001010100017'))
        self.assertTrue(idnumbers.validate('EG', '30002290100011'))
        self.assertFalse(idnumbers.validate('EG', '29002300100017'))
        info = idnumbers.parse_id_info('EG', '29001010100017')
        assert info.ok
        self.assertEqual(date(1990, 1, 1), info.info['yyyymmdd'])
        self.assertEqual('01', info.info['governorate'])

    def test_failure_reasons(self):
        self.assertIsNone(idnumbers.failure_reason(EGY.NationalID, '29001010100017'))
        self.assertEqual(FailureReason.INVALID_BIRTHDATE, idnumbers.failure_reason(EGY.NationalID, '29002300100017'))
        self.assertEqual(FailureReason.INVALID_FORMAT, idnumbers.failure_reason(EGY.NationalID, '2900101010001A'))
