from unittest import TestCase
from idnumbers.nationalid import AUT


class TestAUTValidation(TestCase):
    def test_normal_case(self):
        self.assertTrue(AUT.TaxIDNumber.validate('931736581'))

    def test_error_case(self):
        self.assertFalse(AUT.TaxIDNumber.validate('931736580'))

    def test_tin_cases(self):
        self.assertTrue(AUT.TIN.individual.validate('931736581'))
        self.assertTrue(AUT.TIN.entity.validate('U10223006'))
        self.assertFalse(AUT.TIN.entity.validate('U10223007'))


class TestAUTEntityValidation(TestCase):
    def assert_verdict(self, value, expected):
        self.assertIs(AUT.EntityTaxIDNumber.validate(value), expected)
        self.assertIs(AUT.EntityTaxIDNumber.checksum(value), expected)

    def test_official_and_issue_vectors(self):
        # BMF UID-Konstruktionsregeln (November 2020), Austria sample on page 1;
        # the official source is linked in EntityTaxIDNumber.METADATA.links.
        self.assert_verdict('U10223006', True)
        self.assert_verdict('U10223007', False)
        # Issue #345: the same checksum-correct body must only accept prefix U.
        self.assert_verdict('U02954062', True)
        self.assert_verdict('X02954062', False)

    def test_only_u_prefix(self):
        for prefix in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
            with self.subTest(prefix=prefix):
                self.assert_verdict(prefix + '02954062', prefix == 'U')
        for prefix in ('u', '0', '?', '', 'ATU', 'DEU'):
            with self.subTest(prefix=prefix):
                self.assert_verdict(prefix + '02954062', False)

    def test_supported_separators(self):
        for first in ('', '-', ' '):
            for second in ('', '/', ' '):
                for final_digit, expected in (('2', True), ('3', False)):
                    value = 'U02' + first + '954' + second + '06' + final_digit
                    with self.subTest(value=value):
                        self.assert_verdict(value, expected)
                        self.assert_verdict('X' + value[1:], False)

    def test_malformed_inputs(self):
        malformed = (
            None, 0, True, b'U02954062', [], {},
            '', 'U', 'U0295406', 'U029540622',
            ' U02954062', 'U02954062 ', '\tU02954062', 'U02954062\n', 'U02954062\r\n',
            'U02/954062', 'U02954-062', 'U02--954062', 'U02  954062',
            'U02954//062', 'U02\t954062', 'U02954\n062',
            'U０２９５４０６２', 'U٠٢٩٥٤٠٦٢', 'U0295406２',
        )
        for value in malformed:
            with self.subTest(value=value):
                self.assert_verdict(value, False)

    def test_independent_checksum_vectors(self):
        # Synthetic payloads, not issued UIDs. Independently sum the decimal
        # digits of alternating 1/2-weighted values, then include the BMF +4.
        payloads = ['0000000', '9999999', '1022300', '0295406']
        payloads.extend('{:07d}'.format(value) for value in range(0, 10000000, 7919))
        for payload in payloads:
            products = (int(char) * weight for char, weight in zip(payload, (1, 2, 1, 2, 1, 2, 1)))
            total = 4 + sum(int(char) for product in products for char in str(product))
            expected_digit = (-total) % 10
            accepted_digits = []
            for digit in range(10):
                value = 'U' + payload + str(digit)
                with self.subTest(value=value):
                    self.assert_verdict(value, digit == expected_digit)
                if AUT.EntityTaxIDNumber.validate(value):
                    accepted_digits.append(digit)
            self.assertEqual(accepted_digits, [expected_digit])

    def test_public_aliases_unchanged(self):
        self.assertIs(AUT.TIN.entity, AUT.EntityTaxIDNumber)
        self.assertIs(AUT.TIN.individual, AUT.TaxIDNumber)
        for validator in (AUT.TIN.individual, AUT.NationalID):
            self.assertTrue(validator.validate('931736581'))
            self.assertFalse(validator.validate('931736580'))
            self.assertFalse(validator.validate('U02954062'))
        self.assertFalse(AUT.EntityTaxIDNumber.METADATA.parsable)
        self.assertFalse(hasattr(AUT.EntityTaxIDNumber, 'parse'))
