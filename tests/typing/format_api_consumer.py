"""Strict consumers of all approved formatting API shapes."""
from typing import Optional, Pattern, Tuple

from idnumbers import InputMask, format_id, get_input_mask, normalize_id

normalized: Optional[str] = normalize_id('BR', '111.444.777-35')
formatted: Optional[str] = format_id('BRA', '11144477735')
result: Optional[InputMask] = get_input_mask('TW')
if result is not None:
    country: str = result.country_code
    masks: Tuple[str, ...] = result.masks
    pattern: Pattern[str] = result.pattern
    copy: InputMask = InputMask(country, masks, pattern)
    print(copy.pattern.fullmatch('A123456789'))
print(normalized, formatted)
