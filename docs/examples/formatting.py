"""UI formatting does not imply validation: preserve the country's accepted representation."""
from idnumbers import format_id, normalize_id, validate
from idnumbers.nationalid import CHE

number = CHE.NationalID.METADATA.example
normalized = normalize_id('CH', number)
assert normalized is not None
assert not validate('CH', normalized).is_valid
formatted = format_id('CH', normalized)
assert formatted is not None and validate('CH', formatted).is_valid
assert format_id('SE', '19811218+9876') == '19811218+9876'
assert validate('SE', '19811218+9876').is_valid
