from unittest import TestCase, main
from idnumbers.nationalid import UKR
from idnumbers.nationalid.constant import Gender


class TestUKRTINValidation(TestCase):
    def test_normal_case(self):
        self.assertTrue(UKR.TaxpayerIDNumber.validate('3184710691'))
        self.assertTrue(UKR.TaxpayerIDNumber.validate('3289360690'))

    def test_error_case(self):
        self.assertFalse(UKR.TaxpayerIDNumber.validate('2019503024'))
        self.assertFalse(UKR.TaxpayerIDNumber.validate('019015514'))

    def test_parse(self):
        result = UKR.TaxpayerIDNumber.parse('3184710691')
        self.assertEqual(1987, result['yyyymmdd'].year)
        self.assertEqual(3, result['yyyymmdd'].month)
        self.assertEqual(12, result['yyyymmdd'].day)
        self.assertEqual(Gender.MALE, result['gender'])
        self.assertEqual(1, result['checksum'])

    def test_with_metadata(self):
        self.assertIsNotNone(UKR.TaxpayerIDNumber.METADATA)
        self.assertTrue(UKR.TaxpayerIDNumber.METADATA.parsable)
        self.assertTrue(UKR.TaxpayerIDNumber.METADATA.checksum)


class TestUKREINValidation(TestCase):
    def test_normal_case(self):
        self.assertTrue(UKR.EntityIDNumber.validate('32813827'))

    def test_error_case(self):
        self.assertFalse(UKR.EntityIDNumber.validate('21388124'))
        self.assertFalse(UKR.EntityIDNumber.validate('019015514'))

    def test_second_pass_issue_examples(self):
        # Reported differential examples: https://github.com/identique/idnumbers/issues/312
        for number in ('57334830', '43089360'):
            with self.subTest(number=number):
                self.assert_remainders(number, 10, 10)
                self.assert_check_digit(number, 0)

    def assert_remainders(self, number, first, second):
        # Independent arithmetic with the existing weight selection; #342 is out of scope.
        weights = (7, 1, 2, 3, 4, 5, 6) if number[0] in '3456' else (1, 2, 3, 4, 5, 6, 7)
        digits = [int(digit) for digit in number[:7]]
        self.assertEqual(sum(digit * weight for digit, weight in zip(digits, weights)) % 11, first)
        self.assertEqual(sum(digit * (weight + 2) for digit, weight in zip(digits, weights)) % 11, second)

    def assert_check_digit(self, number, expected):
        # The calculator ignores the supplied check digit; validation must not.
        for digit in range(10):
            candidate = number[:7] + str(digit)
            with self.subTest(candidate=candidate):
                self.assertEqual(UKR.EntityIDNumber.checksum(candidate), expected)
                self.assertEqual(UKR.EntityIDNumber.validate(candidate), digit == expected)

    def test_first_pass_digits_bypass_second_pass(self):
        # Synthetic vectors, ordered by first-pass remainder 0..9 in each weight branch.
        vectors = (
            ('06885270', '06819801', '02838552', '02429983', '07739984',
             '01523355', '01553416', '08994537', '03381178', '07206839'),
            ('65387650', '65956031', '64118692', '65128413', '62052614',
             '67774305', '65463186', '63208617', '68374838', '69383639'),
        )
        second_remainders = ((6, 10, 9, 5, 2, 10, 0, 6, 10, 6), (3, 3, 6, 2, 4, 7, 6, 4, 9, 8))
        for numbers, remainders in zip(vectors, second_remainders):
            for first, (number, second) in enumerate(zip(numbers, remainders)):
                with self.subTest(number=number):
                    self.assert_remainders(number, first, second)
                    self.assert_check_digit(number, first)

    def test_second_pass_remainders(self):
        # Synthetic vectors, ordered by second-pass remainder 0..10 in each weight branch.
        # The 6-prefix branch intentionally preserves legacy selection pending #342.
        vectors = (
            ('03783340', '04004221', '07706812', '08380503', '02497174', '03895475',
             '03337316', '09569537', '03289648', '02054329', '02551900'),
            ('67204360', '67161941', '65496282', '65510433', '63725704', '69440765',
             '65124766', '68231517', '66159058', '61931709', '66555980'),
        )
        for numbers in vectors:
            for second, number in enumerate(numbers):
                with self.subTest(number=number):
                    self.assert_remainders(number, 10, second)
                    self.assert_check_digit(number, second % 10)

    def test_existing_weight_selection(self):
        # Synthetic cases cover non-6 prefixes too, without resolving #342.
        vectors = (
            ('24373668', 8, 4), ('00942268', 8, 10), ('27379469', 10, 9), ('06830790', 10, 10),
            ('54859562', 2, 9), ('38879836', 6, 10), ('64067675', 10, 5), ('56366070', 10, 10),
        )
        for number, first, second in vectors:
            with self.subTest(number=number):
                self.assert_remainders(number, first, second)
                self.assert_check_digit(number, first if first < 10 else second % 10)
        self.assert_check_digit('65908344', 4)

    def test_invalid_input(self):
        for value in (None, 57334830, b'57334830', [], {}, '', '5733483', '573348300',
                      '５７３３４８３０', '٥٧٣٣٤٨٣٠', '57334830\n', ' 57334830', '57334830 ', '5733483X'):
            with self.subTest(value=value):
                self.assertFalse(UKR.EntityIDNumber.validate(value))
                self.assertIsNone(UKR.EntityIDNumber.checksum(value))

    def test_with_metadata(self):
        self.assertIsNotNone(UKR.EntityIDNumber.METADATA)
        self.assertFalse(UKR.EntityIDNumber.METADATA.parsable)
        self.assertTrue(UKR.EntityIDNumber.METADATA.checksum)


if __name__ == '__main__':
    main()
