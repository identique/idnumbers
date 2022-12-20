from re import Pattern


def validate_regexp(id_number: str, regexp: Pattern[str]) -> bool:
    assert isinstance(id_number, str), 'id_number MUST be str'
    return regexp.search(id_number) is not None
