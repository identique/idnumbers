from unittest import TestCase, main
from idnumbers.nationalid import DEU


class TestDEUNationalIDValidation(TestCase):
    def test_normal_case(self):
        self.assertTrue(DEU.TaxID.validate('65929970489'))
        self.assertTrue(DEU.TaxID.validate('26954371827'))
        self.assertTrue(DEU.TaxID.validate('86095742719'))

    def test_error_case(self):
        self.assertFalse(DEU.TaxID.validate('65299970480'))
        self.assertFalse(DEU.TaxID.validate('26954371820'))

    def test_valid_vectors(self):
        vectors = [
            # ELSTER Tabelle 2-1 (section 2.2) examples
            '86095742719', '47036892816', '65929970489', '57549285017', '25768131411',
            # existing vector
            '26954371827',
            # constructed: triple 9 not consecutive, triple 9 with one adjacent pair, double 9 at positions 9-10 with
            # a check digit of 9 (the check digit must not count towards the consecutive rule)
            '19239456987', '12993456781', '38056471999',
            # with spaces
            '65 929 970 489',
        ]
        for klass in (DEU.TaxID, DEU.NationalID, DEU.IdNr):
            for vector in vectors:
                with self.subTest(klass=klass.__name__, vector=vector):
                    self.assertTrue(klass.validate(vector))

    def test_invalid_vectors(self):
        vectors = [
            # issue #289: leading 0, digit 9 four times in the first 10 digits
            '04585675199', '39825979193',
            # ELSTER test IdNr (leading 0)
            '02476291358',
            # constructed: digit 9 four times, no repeated digit, two different doubled digits, triple 9 consecutive
            '91293949567', '36794081522', '11234566772', '12345699902',
            # with spaces
            '04 585 675 199',
        ]
        for klass in (DEU.TaxID, DEU.NationalID, DEU.IdNr):
            for vector in vectors:
                with self.subTest(klass=klass.__name__, vector=vector):
                    self.assertFalse(klass.validate(vector))

    def test_invalid_by_digit_rules_have_correct_check_digit(self):
        # constructed vectors (issue #289 for the first): the check digit is right, so only the digit rules reject them
        for vector in ('39825979193', '91293949567', '36794081522', '11234566772', '12345699902'):
            with self.subTest(vector=vector):
                self.assertTrue(DEU.TaxID.checksum(vector))
                self.assertFalse(DEU.TaxID.validate(vector))

    def test_leading_zero_is_not_well_formed(self):
        self.assertFalse(DEU.TaxID.checksum('02476291358'))


if __name__ == '__main__':
    main()
