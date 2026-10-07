# /// script
# requires-python = ">=3.9"
# dependencies = ["idnumbers"]
# ///
"""Run with ``uv run docs/examples/uv_script.py`` (see the uv scripts guide).

https://docs.astral.sh/uv/guides/scripts/ explains the inline dependency metadata.
Vectors are from tests/nationalid/test_{TWN,CHN,ZAF}.py; validation checks
structure/checksum, not proof that an ID was issued to a real person.
"""

from datetime import date

from idnumbers.nationalid import CHN, TWN, ZAF
from idnumbers.nationalid.constant import Citizenship, Gender


def main() -> None:
    examples = (
        (TWN.NationalID, 'A123456789', {'location': 'A', 'gender': Gender.MALE,
                                      'sn': '2345678', 'checksum': 9}),
        (CHN.ResidentID, '372925199510103222', {'address_code': '372925', 'yyyymmdd': date(1995, 10, 10),
                                             'sn': '322', 'gender': Gender.FEMALE, 'checksum': 2}),
        (ZAF.NationalID, '7605300675088', {'yyyymmdd': date(1976, 5, 30), 'sn': '0675',
                                        'gender': Gender.FEMALE, 'citizenship': Citizenship.CITIZEN,
                                        'checksum': 8}),
    )
    for validator, number, expected in examples:
        if validator.validate(number) is not True or validator.parse(number) != expected:
            raise RuntimeError('Unexpected validation/parse result for ' + number)
    print('Validated and parsed TWN, CHN and ZAF examples.')


if __name__ == '__main__':
    main()
