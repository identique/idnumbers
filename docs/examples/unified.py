"""Primary lookup/parse and an explicitly selected secondary ID, using synthetic metadata examples."""
from idnumbers import FailureReason, ParseSuccess, failure_reason, parse_id_info, validate_many
from idnumbers.nationalid import AUS

parsed = parse_id_info('TW', 'A123456789')
assert isinstance(parsed, ParseSuccess)
assert parsed.country_code == 'TWN'
assert parsed.info['location'] == 'A'
results = validate_many([('TW', 'A123456789'), ('XX', '1')])
assert [result.is_valid for result in results] == [True, False]
assert results[1].reason == FailureReason.UNSUPPORTED_COUNTRY
assert AUS.MedicareNumber.validate(AUS.MedicareNumber.METADATA.example)
assert failure_reason(AUS.MedicareNumber, AUS.MedicareNumber.METADATA.example) is None
