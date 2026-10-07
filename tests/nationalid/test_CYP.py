from unittest import TestCase

from idnumbers.nationalid.CYP import NationalID, TaxNumber, TIN


class TestCYPTaxNumberValidation(TestCase):
    ALIASES = (('TaxNumber', TaxNumber), ('NationalID', NationalID),
               ('TIN.individual', TIN.individual), ('TIN.entity', TIN.entity))

    def test_normal_case(self):
        # Existing examples from the EU TIN algorithm document cited in checksum().
        self.assertTrue(TIN.individual.validate('00123123T'))
        self.assertTrue(TIN.individual.validate('99652156X'))

    def test_error_case(self):
        self.assertFalse(TIN.individual.validate('00123123A'))
        self.assertFalse(TIN.individual.validate('99652156B'))

    def test_forbidden_prefix_with_correct_checksum(self):
        # Synthetic arithmetic fixtures; prefix 12 is excluded by python-stdnum 2.2 cy/vat.py.
        for name, validator in self.ALIASES:
            for number in ('12345678F', '12000000F'):
                with self.subTest(alias=name, number=number):
                    self.assertFalse(validator.validate(number))
                    self.assertTrue(validator.checksum(number))

    def test_forbidden_prefix_with_every_check_letter(self):
        for name, validator in self.ALIASES:
            for digits in ('12345678', '12000000'):
                for letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
                    with self.subTest(alias=name, digits=digits, letter=letter):
                        self.assertFalse(validator.validate(digits + letter))
                        self.assertEqual(validator.checksum(digits + letter), letter == 'F')

    def test_other_prefixes_keep_checksum_validation(self):
        # Synthetic fixtures exercise neighboring prefixes and avoid imposing a 0/9/6 whitelist.
        numbers = ('11000000E', '13000000G', '60000000S', '00000000E', '90000000Y',
                   '10000000D', '20000000I', '50000000Q', '99000000H')
        for name, validator in self.ALIASES:
            for number in numbers:
                with self.subTest(alias=name, number=number):
                    self.assertTrue(validator.validate(number))
                    self.assertTrue(validator.checksum(number))
                    self.assertFalse(validator.validate(number[:-1] + 'A'))
                    self.assertFalse(validator.checksum(number[:-1] + 'A'))

    def test_malformed_input_is_rejected(self):
        numbers = (None, False, 0, 12345678, [], {}, b'12345678F', '', '1234567F',
                   '123456789F', '12345678f', '12345678', 'CY12345678F', '12345678F\n',
                   ' 12345678F', '12345678F ', '１２３４５６７８F', '١٢٣٤٥٦٧٨F',
                   '60000000S\n', '６０００００００S', '12345678ſ')
        for name, validator in self.ALIASES:
            for number in numbers:
                with self.subTest(alias=name, number=number):
                    self.assertFalse(validator.validate(number))
                    self.assertFalse(validator.checksum(number))

    def test_individual_classification_is_unchanged(self):
        for name, validator in self.ALIASES:
            for number, expected in (('00123123T', True), ('99652156X', True),
                                     ('12000000F', False), ('60000000S', False),
                                     ('11000000E', False), ('13000000G', False)):
                with self.subTest(alias=name, number=number):
                    self.assertEqual(validator.is_individual(number), expected)
