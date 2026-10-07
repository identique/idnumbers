from unittest import TestCase, main
from idnumbers.nationalid import NZL


class TestNZLDriverLicenseNumberValidation(TestCase):
    def test_normal_case(self):
        self.assertTrue(NZL.DriverLicenseNumber.validate('AA345678'))
        self.assertTrue(NZL.DriverLicenseNumber.validate('aa123456'))

    def test_error_case(self):
        self.assertFalse(NZL.DriverLicenseNumber.validate('12-345-678'))
        self.assertFalse(NZL.DriverLicenseNumber.validate('AA000000'))
        self.assertFalse(NZL.DriverLicenseNumber.validate('B11111'))

    def test_prefix_is_ascii_letters_only(self):
        self.assertTrue(NZL.DriverLicenseNumber.validate('AB123456'))
        # Latin letter with a diaeresis and Greek capitals look like letters but are not ASCII
        self.assertFalse(NZL.DriverLicenseNumber.validate('\u00c4B123456'))
        self.assertFalse(NZL.DriverLicenseNumber.validate('\u0391\u0392123456'))

    def test_strict_format_and_input_contract(self):
        for value in ('_B123456', '12345678', 'A1123456', 'AB１２３４５６',
                      'AB123456\n', '', None, 12345678, [], {}):
            with self.subTest(value=value):
                self.assertFalse(NZL.DriverLicenseNumber.validate(value))
                self.assertFalse(NZL.NationalID.validate(value))
        for value in ('IO123456', 'io123456', 'Ab123456'):
            with self.subTest(value=value):
                self.assertTrue(NZL.DriverLicenseNumber.validate(value))
                self.assertIsNotNone(NZL.DriverLicenseNumber.METADATA.regexp.fullmatch(value))
        for value in ('_B123456', '12345678', 'A1123456', 'ÄB123456', 'AB１２３４５６'):
            with self.subTest(value=value):
                self.assertIsNone(NZL.DriverLicenseNumber.METADATA.regexp.fullmatch(value))
        for digit in '0123456789':
            self.assertFalse(NZL.DriverLicenseNumber.validate('AB' + digit * 6))

    def test_with_metadata(self):
        self.assertIsNotNone(NZL.DriverLicenseNumber.METADATA)


class TestNZLPassportNumberValidation(TestCase):
    def test_normal_case(self):
        self.assertTrue(NZL.PassportNumber.validate('La615098'))
        self.assertTrue(NZL.PassportNumber.validate('LD615098'))
        self.assertTrue(NZL.PassportNumber.validate('lF615098'))
        self.assertTrue(NZL.PassportNumber.validate('n615098'))
        self.assertTrue(NZL.PassportNumber.validate('ea615098'))
        self.assertTrue(NZL.PassportNumber.validate('LH615098'))

    def test_error_case(self):
        self.assertFalse(NZL.PassportNumber.validate('12-345-678'))
        self.assertFalse(NZL.PassportNumber.validate('LH000000'))
        self.assertFalse(NZL.PassportNumber.validate('B11111'))

    def test_with_metadata(self):
        self.assertEqual(NZL.PassportNumber.METADATA.names, ['Passport Number'])


class TestNZLIRDValidation(TestCase):
    def test_normal_case(self):
        self.assertTrue(NZL.InlandRevenueDepartmentNumber.validate('49091850'))
        self.assertTrue(NZL.InlandRevenueDepartmentNumber.validate('35901981'))
        self.assertTrue(NZL.InlandRevenueDepartmentNumber.validate('136410132'))
        self.assertTrue(NZL.InlandRevenueDepartmentNumber.validate('49-091-850'))
        self.assertTrue(NZL.InlandRevenueDepartmentNumber.validate('35-901-981'))
        self.assertTrue(NZL.InlandRevenueDepartmentNumber.validate('136-410-132'))

    def test_error_case(self):
        self.assertFalse(NZL.InlandRevenueDepartmentNumber.validate('49091851'))
        self.assertFalse(NZL.InlandRevenueDepartmentNumber.validate('35901982'))
        self.assertFalse(NZL.InlandRevenueDepartmentNumber.validate('136410133'))
        self.assertFalse(NZL.InlandRevenueDepartmentNumber.validate('49 091 850'))
        self.assertFalse(NZL.InlandRevenueDepartmentNumber.validate('35.901.981'))
        self.assertFalse(NZL.InlandRevenueDepartmentNumber.validate('136/410/132'))

    def test_official_checksum_examples(self):
        # IRD's 2026 overseas pension transfers specification, section 5.3.
        for value in ('49091850', '35901981', '49098576', '136410132'):
            with self.subTest(value=value):
                self.assertTrue(NZL.InlandRevenueDepartmentNumber.validate(value))
                self.assertTrue(NZL.InlandRevenueDepartmentNumber.checksum(value))

    def test_numeric_range(self):
        # Synthetic checksum-correct numbers, not issued numbers. The current
        # upper limit is 200 million, not the superseded 150 million limit.
        for value in ('150000009', '150-000-009', '199999990', '199-999-990'):
            with self.subTest(value=value):
                self.assertTrue(NZL.InlandRevenueDepartmentNumber.validate(value))
                self.assertTrue(NZL.InlandRevenueDepartmentNumber.checksum(value))
        for value in ('000000000', '000-000-000', '00000000', '00-000-000',
                      '009999996', '009-999-996', '09999996', '09-999-996',
                      '200000005', '200-000-005'):
            with self.subTest(value=value):
                self.assertFalse(NZL.InlandRevenueDepartmentNumber.validate(value))
                self.assertFalse(NZL.InlandRevenueDepartmentNumber.checksum(value))
        # Range endpoints still require a correct check digit.
        for value in ('10000000', '10-000-000', '200000000', '200-000-000'):
            with self.subTest(value=value):
                self.assertFalse(NZL.InlandRevenueDepartmentNumber.validate(value))
                self.assertFalse(NZL.InlandRevenueDepartmentNumber.checksum(value))

    def test_with_metadata(self):
        self.assertIsNotNone(NZL.InlandRevenueDepartmentNumber.METADATA)


class TestNZLNHIValidation(TestCase):
    def test_normal_case(self):
        self.assertTrue(NZL.NationalHealthIndexNumber.validate('ZZZ0016'))
        self.assertTrue(NZL.NationalHealthIndexNumber.validate('ZZZ0024'))
        self.assertTrue(NZL.NationalHealthIndexNumber.validate('ZZZ00AC'))
        self.assertTrue(NZL.NationalHealthIndexNumber.validate('ALU18KP'))

    def test_error_case(self):
        self.assertFalse(NZL.NationalHealthIndexNumber.validate('ZZZ0017'))
        self.assertFalse(NZL.NationalHealthIndexNumber.validate('ZZZ00AZ'))
        self.assertFalse(NZL.NationalHealthIndexNumber.validate('ALU28KZ'))

    def test_official_expanded_format_vectors(self):
        # HISO 10046:2024 Table 3 and Health NZ's published compliance test data:
        # https://nhi-ig.hip.digital.health.nz/ComplianceTestingImportantInformation.html
        # Expanded-format implementation is planned for 1 July 2027; these are
        # test vectors, not a claim that expanded numbers have been issued.
        values = ('ZBN77VL', 'ZXE24NV', 'ZUA48EH', 'ZUT01RG', 'ZNK28DJ',
                  'ZTL39SK', 'ZWB84LW', 'ZQF54PV', 'ZAK21MS', 'ZYC49PX',
                  'ZDP92ZR', 'ZVE74QH')
        for value in values:
            with self.subTest(value=value):
                self.assertTrue(NZL.NationalHealthIndexNumber.validate(value))
                self.assertTrue(NZL.NationalHealthIndexNumber.checksum(value))
            for check_letter in 'ABCDEFGHJKLMNPQRSTUVWXYZ':
                if check_letter != value[-1]:
                    with self.subTest(value=value, check_letter=check_letter):
                        self.assertFalse(NZL.NationalHealthIndexNumber.validate(value[:-1] + check_letter))
        self.assertTrue(NZL.NationalHealthIndexNumber.validate('ZAC5361'))

    def test_expanded_modulus_boundaries(self):
        # Synthetic weighted sums 23 and 45 have remainders 0 and 22 modulo 23.
        # The 1-based check-letter indices are 23 (Y) and 1 (A); never 24 (Z).
        for value in ('AAA01AY', 'AAA17AA'):
            with self.subTest(value=value):
                self.assertTrue(NZL.NationalHealthIndexNumber.validate(value))
                self.assertTrue(NZL.NationalHealthIndexNumber.checksum(value))
        for value in ('AAA01AZ', 'AAA17AZ', 'ZZZ00AX', 'ALU18KZ'):
            with self.subTest(value=value):
                self.assertFalse(NZL.NationalHealthIndexNumber.validate(value))
                self.assertFalse(NZL.NationalHealthIndexNumber.checksum(value))

    def test_with_metadata(self):
        self.assertIsNotNone(NZL.NationalHealthIndexNumber.METADATA)


if __name__ == '__main__':
    main()
