from unittest import TestCase

import idnumbers
from idnumbers.nationalid import ECU


def mod10_digit(first_nine: str) -> int:
    """independent implementation of the check digit, weights 2,1,2,1,2,1,2,1,2"""
    total = 0
    for index, char in enumerate(first_nine):
        product = int(char) * (2 if index % 2 == 0 else 1)
        total += product - 9 if product > 9 else product
    return (10 - total % 10) % 10


class TestECUValidation(TestCase):
    def test_country_metadata(self):
        self.assertEqual(ECU.NationalID.METADATA.iso3166_alpha2, 'EC')
        self.assertEqual(ECU.NationalID.METADATA.country_name, 'Ecuador')
        self.assertTrue(ECU.NationalID.METADATA.checksum)
        self.assertTrue(ECU.NationalID.validate(ECU.NationalID.METADATA.example))

    def test_normal_case(self):
        for id_number in (
            '1710000009',  # Node port test vector
            '0900000001',  # Node port test vector
            '3040000006',  # Node port test vector
            '3050000003',  # Node port test vector
            '1700000050',  # Node port test vector
            '2450000001',  # Node port test vector
            '171000000-9',  # Node port test vector, hyphen before the check digit
            '1714307103',  # python-stdnum doctest example
            '171430710-3',  # python-stdnum doctest example
            # public test cédulas of the SNAP instructivo for the series 30 (September 2015)
            '3040040382',
            '3040123386',
            '3044223182',
            '3043223183',
            '3042233274',
            '0960000008',  # synthetic, third digit 6 (Gob.EC issue 597)
            '1760000008',  # synthetic, third digit 6
            '2400000002',  # synthetic, last province
            '0100000009',  # synthetic, first province
        ):
            with self.subTest(id_number=id_number):
                self.assertTrue(ECU.NationalID.validate(id_number))

    def test_error_case(self):
        for id_number in (
            '1710000000',  # wrong check digit
            '1714307104',  # wrong check digit
            '3040040383',  # wrong check digit, province 30
            '2510000009',  # province 25
            '0010000008',  # province 00 with a valid check digit
            '3110000007',  # province 31
            '1770000006',  # third digit 7
            '1780000004',  # third digit 8
            '1790000002',  # third digit 9
            '5010000007',  # province 50: accepted by python-stdnum, deliberately rejected
            '3000000004',  # province 30 with third digit 0: accepted by python-stdnum, deliberately rejected
            '3010000002',  # province 30 with third digit 1
            '3060000001',  # province 30 with third digit 6 and a valid check digit
            '171000000',  # 9 digits
            '17100000099',  # 11 digits
            '171000000 9',  # space
            ' 1710000009',  # leading space
            '17-10000009',  # hyphen elsewhere
            '171-0000009',  # hyphen elsewhere
            '171000000--9',
            '1710000009-',
            '-1710000009',
            '1710000009\n',  # trailing newline
            '171000000-9\n',
            '１７１００００００９',  # full-width digits
            '171000000A',
            '',
        ):
            with self.subTest(id_number=id_number):
                self.assertFalse(ECU.NationalID.validate(id_number))
                self.assertIsNone(ECU.NationalID.parse(id_number))

    def test_non_string_input(self):
        for value in (None, 1710000009):
            with self.subTest(value=value):
                self.assertFalse(ECU.NationalID.validate(value))  # type: ignore[arg-type]
                self.assertIsNone(ECU.NationalID.parse(value))  # type: ignore[arg-type]
                self.assertIsNone(ECU.NationalID.checksum(value))  # type: ignore[arg-type]

    def test_parse(self):
        self.assertEqual({'province': '17', 'sequence_number': '000000', 'checksum': 9},
                         ECU.NationalID.parse('171000000-9'))
        self.assertEqual(ECU.NationalID.parse('171000000-9'), ECU.NationalID.parse('1710000009'))
        self.assertEqual({'province': '30', 'sequence_number': '004038', 'checksum': 2},
                         ECU.NationalID.parse('3040040382'))
        self.assertEqual({'province': '09', 'sequence_number': '000000', 'checksum': 8},
                         ECU.NationalID.parse('0960000008'))

    def test_checksum(self):
        self.assertEqual(9, ECU.NationalID.checksum('1710000009'))
        self.assertEqual(9, ECU.NationalID.checksum('171000000-9'))
        self.assertEqual(3, ECU.NationalID.checksum('1714307103'))
        # the computed digit does not depend on the number's own last digit ...
        self.assertEqual(9, ECU.NationalID.checksum('1710000000'))
        self.assertEqual(3, ECU.NationalID.checksum('1714307104'))
        # ... nor on the third-digit rule, which only validate() applies
        self.assertEqual(6, ECU.NationalID.checksum('1770000000'))
        self.assertEqual(4, ECU.NationalID.checksum('3000000000'))
        for id_number in ('', '171000000', '17100000099', '171000000 9', '1710000009\n', '171000000A',
                          '2510000009', '0010000008'):
            with self.subTest(id_number=id_number):
                self.assertIsNone(ECU.NationalID.checksum(id_number))

    def test_every_check_digit_is_unique(self):
        # for a fixed prefix exactly one of the ten possible last digits is valid
        for prefix in ('171000000', '171430710', '304004038', '096000000'):
            valid = [digit for digit in range(10) if ECU.NationalID.validate('%s%d' % (prefix, digit))]
            self.assertEqual([ECU.NationalID.checksum(prefix + '0')], valid)

    def test_third_digit_rules(self):
        for third in range(10):
            province_17 = '17%d000000' % third
            province_30 = '30%d000000' % third
            for prefix, allowed in ((province_17, third <= 6), (province_30, third in (4, 5))):
                with self.subTest(prefix=prefix):
                    self.assertEqual(allowed, ECU.NationalID.validate('%s%d' % (prefix, mod10_digit(prefix))))

    def test_province_range(self):
        # third digit 1 is accepted for the provinces 01-24 only; 30 needs a third digit 4 or 5
        for province in range(100):
            prefix = '%02d1000000' % province
            with self.subTest(province=province):
                self.assertEqual(1 <= province <= 24, ECU.NationalID.validate('%s%d' % (prefix, mod10_digit(prefix))))

    def test_unified_api(self):
        self.assertTrue(idnumbers.validate('ECU', '1710000009'))
        self.assertTrue(idnumbers.validate('EC', '171000000-9'))
        self.assertFalse(idnumbers.validate('EC', '1710000000'))
        self.assertFalse(idnumbers.validate('EC', '5010000007'))
        info = idnumbers.parse_id_info('EC', '171000000-9')
        assert info.ok
        self.assertEqual('17', info.info['province'])
        self.assertEqual(9, info.info['checksum'])
