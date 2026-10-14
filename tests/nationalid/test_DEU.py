from unittest import TestCase, main
from idnumbers.nationalid import DEU


class TestDEUNationalIDValidation(TestCase):
    def test_normal_case(self):
        self.assertTrue(DEU.TaxID.validate("65929970489"))
        self.assertTrue(DEU.TaxID.validate("26954371827"))
        self.assertTrue(DEU.TaxID.validate("86095742719"))

    def test_error_case(self):
        self.assertFalse(DEU.TaxID.validate("65299970480"))
        self.assertFalse(DEU.TaxID.validate("26954371820"))

    def test_valid_vectors(self):
        vectors = [
            # ELSTER Tabelle 2-1 (section 2.2) examples
            "86095742719",
            "47036892816",
            "65929970489",
            "57549285017",
            "25768131411",
            # existing vector
            "26954371827",
            # constructed: triple 9 not consecutive, double 9 as an adjacent pair, triple 9 with one adjacent pair
            # (check digit computed with TaxID.get_checkdigit), double 9 at positions 9-10 with a check digit of 9
            # (the check digit must not count towards the consecutive rule)
            "19239456987",
            "12993456781",
            "12993456790",
            "38056471999",
            # with spaces
            "65 929 970 489",
        ]
        for klass in (DEU.TaxID, DEU.NationalID, DEU.IdNr):
            for vector in vectors:
                with self.subTest(klass=klass.__name__, vector=vector):
                    self.assertTrue(klass.validate(vector))

    def test_invalid_vectors(self):
        vectors = [
            # issue #289: leading 0, digit 9 four times in the first 10 digits
            "04585675199",
            "39825979193",
            # ELSTER test IdNr (leading 0)
            "02476291358",
            # constructed: digit 9 four times, no repeated digit, two different doubled digits, triple 9 consecutive
            "91293949567",
            "36794081522",
            "11234566772",
            "12345699902",
            # with spaces
            "04 585 675 199",
        ]
        for klass in (DEU.TaxID, DEU.NationalID, DEU.IdNr):
            for vector in vectors:
                with self.subTest(klass=klass.__name__, vector=vector):
                    self.assertFalse(klass.validate(vector))

    def test_invalid_by_digit_rules_have_correct_check_digit(self):
        # constructed vectors (issue #289 for the first): the check digit is right, so only the digit rules reject them
        for vector in ("39825979193", "91293949567", "36794081522", "11234566772", "12345699902"):
            with self.subTest(vector=vector):
                self.assertTrue(DEU.TaxID.checksum(vector))
                self.assertFalse(DEU.TaxID.validate(vector))

    def test_constructed_triple_with_adjacent_pair(self):
        # '12993456781' holds a double 9 in its first ten digits; '12993456790' is the triple 9 with one adjacent pair
        self.assertEqual("1299345678".count("9"), 2)
        self.assertEqual("1299345679".count("9"), 3)
        self.assertIn("99", "1299345679")
        self.assertNotIn("999", "1299345679")
        self.assertEqual(DEU.TaxID.get_checkdigit([int(c) for c in "1299345679"]), 0)
        self.assertTrue(DEU.TaxID.checksum("12993456790"))

    def test_leading_zero_is_not_well_formed(self):
        self.assertFalse(DEU.TaxID.checksum("02476291358"))


class TestDEUTaxNumberValidation(TestCase):
    # ELSTER Tabelle 4-1: test numbers in the ELSTER format, one or more per federal state
    ELSTER_VECTORS = {
        "2866081508156": "DE-BW",
        "9198081508152": "DE-BY",
        "9296081508153": "DE-BY",
        "1197081508154": "DE-BE",
        "3098081508157": "DE-BB",
        "2497012301233": "DE-HB",
        "2293081508150": "DE-HH",
        "2653081508158": "DE-HE",
        "4098081508157": "DE-MV",
        "2388081508158": "DE-NI",
        "5400081508159": "DE-NW",
        "5500081508151": "DE-NW",
        "5600081508154": "DE-NW",
        "2799081508152": "DE-RP",
        "1096081508187": "DE-SL",
        "3248081508156": "DE-SN",
        "3198081508152": "DE-ST",
        "2138081508154": "DE-SH",
        "4198081508152": "DE-TH",
    }

    def test_elster_vectors(self):
        for klass in (DEU.TaxNumber, DEU.Steuernummer):
            for vector, state in self.ELSTER_VECTORS.items():
                with self.subTest(klass=klass.__name__, vector=vector):
                    self.assertTrue(klass.validate(vector))
                    self.assertTrue(klass.checksum(vector))
                    self.assertEqual(state, klass.parse(vector)["state"])

    def test_wrong_check_digit(self):
        for vector in self.ELSTER_VECTORS:
            for check_digit in "0123456789":
                if check_digit == vector[-1]:
                    continue
                with self.subTest(vector=vector, check_digit=check_digit):
                    self.assertFalse(DEU.TaxNumber.validate(vector[:-1] + check_digit))
                    self.assertFalse(DEU.TaxNumber.checksum(vector[:-1] + check_digit))

    def test_parse(self):
        self.assertEqual(
            {
                "state": "DE-BY",
                "tax_office": "9198",
                "district": "815",
                "distinguishing_number": "0815",
                "checksum": 2,
            },
            DEU.TaxNumber.parse("9198081508152"),
        )
        # North Rhine-Westphalia: 4-digit district and 3-digit distinguishing number
        self.assertEqual(
            {
                "state": "DE-NW",
                "tax_office": "5400",
                "district": "8150",
                "distinguishing_number": "815",
                "checksum": 9,
            },
            DEU.TaxNumber.parse("5400081508159"),
        )
        self.assertIsNone(DEU.TaxNumber.parse("9198081508153"))
        self.assertIsNone(DEU.TaxNumber.parse(None))

    def test_format(self):
        vectors = [
            # the format printed on tax notices is not accepted
            "198/815/08152",
            "19881508152",
            # 5th digit is not 0
            "9198181508152",
            # unknown state number (25, 29, 33, 42, 6, 7, 8, 0)
            "2598081508152",
            "2998081508152",
            "3398081508152",
            "4298081508152",
            "6198081508152",
            "7198081508152",
            "8198081508152",
            "0198081508152",
            # length, separators, letters and empty input
            "919808150815",
            "91980815081520",
            "9198 0815 08152",
            "919808150815A",
            "",
        ]
        for vector in vectors:
            with self.subTest(vector=vector):
                self.assertFalse(DEU.TaxNumber.validate(vector))
                self.assertFalse(DEU.TaxNumber.checksum(vector))
        self.assertFalse(DEU.TaxNumber.validate(None))
        self.assertFalse(DEU.TaxNumber.checksum(None))

    def test_district_rules(self):
        # constructed: the check digit is right, so only the district rules reject them
        vectors = [
            # district 000, 998 and 999 (0999 in North Rhine-Westphalia)
            "9198000008150",
            "9198099808153",
            "5400009990820",
            # district under 100 in the Bavarian programming group (Bavaria, Brandenburg)
            "9198009908154",
            "3098009908159",
            # North Rhine-Westphalia: distinguishing number and check digit not greater than 0009
            "5400000100006",
        ]
        for vector in vectors:
            with self.subTest(vector=vector):
                self.assertTrue(DEU.TaxNumber.checksum(vector))
                self.assertFalse(DEU.TaxNumber.validate(vector))
        # a district under 100 is allowed outside the Bavarian programming group (Bremen); 0010 is allowed in NRW
        self.assertTrue(DEU.TaxNumber.validate("2497000108152"))
        self.assertTrue(DEU.TaxNumber.validate("5400000100017"))

    def test_two_digit_check_digit_is_never_allocated(self):
        # constructed: the 11er-Verfahren gives 10 for these first 12 digits, so no check digit is valid
        for prefix in ("919808150002", "540008150018", "111301000008"):
            for check_digit in "0123456789":
                with self.subTest(prefix=prefix, check_digit=check_digit):
                    self.assertFalse(DEU.TaxNumber.validate(prefix + check_digit))

    def test_berlin_weights(self):
        # constructed: Berlin-A and Berlin-B give different check digits for these first 12 digits
        # 1113 uses Berlin-A, and Berlin-B for districts 201 to 693
        self.assertTrue(DEU.TaxNumber.validate("1113010000004"))
        self.assertFalse(DEU.TaxNumber.validate("1113010000007"))
        self.assertTrue(DEU.TaxNumber.validate("1113020100004"))
        self.assertFalse(DEU.TaxNumber.validate("1113020100003"))
        # 1115 always uses Berlin-B
        self.assertTrue(DEU.TaxNumber.validate("1115010000000"))
        self.assertFalse(DEU.TaxNumber.validate("1115010000004"))
        # 1116 uses Berlin-B for districts 1 to 29, 201 to 693 and 875 to 899
        self.assertTrue(DEU.TaxNumber.validate("1116001000003"))
        self.assertFalse(DEU.TaxNumber.validate("1116001000005"))
        self.assertTrue(DEU.TaxNumber.validate("1116010000004"))
        self.assertFalse(DEU.TaxNumber.validate("1116010000002"))
        # 1119 uses Berlin-B for district 680, but Berlin-A for 681
        self.assertTrue(DEU.TaxNumber.validate("1119068000000"))
        self.assertFalse(DEU.TaxNumber.validate("1119068000009"))
        self.assertTrue(DEU.TaxNumber.validate("1119068100004"))
        self.assertFalse(DEU.TaxNumber.validate("1119068100005"))
        # a Berlin tax office missing from the ELSTER table may use either
        self.assertTrue(DEU.TaxNumber.validate("1101010000004"))
        self.assertTrue(DEU.TaxNumber.validate("1101010000005"))
        self.assertFalse(DEU.TaxNumber.validate("1101010000006"))


if __name__ == "__main__":
    main()
