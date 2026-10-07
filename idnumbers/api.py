"""
One entry point to validate an ID number of any supported country.

:func:`validate` takes the code of a country and an ID number, and returns a :class:`ValidationResult` that says
whether the ID number is valid, which country was used, what the ID number contains and why it failed. It never
raises: an unknown country, a malformed ID number and an unexpected error inside a validator all give a result with
``is_valid`` set to ``False``. The country is found with :func:`idnumbers.registry.resolve_country`, so an alpha-2
or alpha-3 code in any letter case works. The ID number is validated exactly as given, without any normalization.

The country classes of :mod:`idnumbers.nationalid` are unchanged, and :func:`validate` uses the ``NationalID`` of the
country. Importing :mod:`idnumbers` stays cheap, as the country module is imported on the first call that needs it.

Example::

    from idnumbers import validate

    result = validate('tw', 'A123456789')
    result.is_valid             # True
    result.country_code         # 'TWN'
    result.extracted_info       # {'location': 'A', 'gender': <Gender.MALE: 'male'>, 'sn': '2345678', 'checksum': 9}

    result = validate('TWN', 'A123456780')
    bool(result)                # False
    result.reason               # <FailureReason.VALIDATION_FAILED: 'validation_failed'>
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Iterable, List, Mapping, Optional, Tuple

from . import registry

__all__ = ['FailureReason', 'ValidationResult', 'validate', 'validate_many']


class FailureReason(str, Enum):
    """
    Why the validation of an ID number failed.

    The set of reasons is not exhaustive: later releases may add values, so don't match it exhaustively.
    """

    UNSUPPORTED_COUNTRY = 'unsupported_country'
    """The country code is unknown, or it isn't a ``str``."""

    INVALID_LENGTH = 'invalid_length'
    """The ID number has a length the ID type doesn't allow. Not produced yet: issue #322 adds it."""

    INVALID_FORMAT = 'invalid_format'
    """The ID number doesn't have the format of the ID type. Not produced yet: issue #322 adds it."""

    CHECKSUM_MISMATCH = 'checksum_mismatch'
    """The check digit or check characters are wrong. Not produced yet: issue #322 adds it."""

    INVALID_BIRTHDATE = 'invalid_birthdate'
    """The birth date inside the ID number isn't a real date. Not produced yet: issue #322 adds it."""

    VALIDATION_FAILED = 'validation_failed'
    """The validator rejected the ID number without a more precise reason, or it raised an exception."""

    NOT_PARSABLE = 'not_parsable'
    """The ID type of the country can't be parsed. Only ``parse_id_info()`` (issue #319) produces it."""


@dataclass(frozen=True)
class ValidationResult:
    """The outcome of validating one ID number. Instances are immutable, and a result is truthy when it is valid."""

    is_valid: bool
    """``True`` when the ID number is valid."""

    country_code: Optional[str]
    """The resolved ISO 3166-1 alpha-3 code, such as ``'TWN'`` for ``'tw'``, or ``None`` for an unsupported country."""

    id_number: str
    """The ID number exactly as it was passed in."""

    extracted_info: Optional[Mapping[str, Any]] = None
    """The ``parse()`` result of a valid ID number, or ``None`` when it is invalid or the ID type isn't parsable."""

    reason: Optional[FailureReason] = None
    """Why the validation failed. It is set if and only if ``is_valid`` is ``False``."""

    error_message: Optional[str] = None
    """The detail of an unsupported country, or of an exception raised by a validator or a parser, else ``None``."""

    def __bool__(self) -> bool:
        return self.is_valid


def validate(country: str, id_number: str) -> ValidationResult:
    """
    Validate an ID number of a country.

    :param country: an ISO 3166-1 alpha-2 or alpha-3 code, or a registered alias, in any letter case.
    :param id_number: the ID number, validated exactly as given.
    :return: a :class:`ValidationResult`. This function never raises.
    """
    alpha3 = registry.resolve_country(country)
    validator = None if alpha3 is None else registry.get_validator(alpha3)
    if alpha3 is None or validator is None:
        return ValidationResult(
            is_valid=False,
            country_code=None,
            id_number=id_number,
            reason=FailureReason.UNSUPPORTED_COUNTRY,
            error_message='unsupported country: %r' % (country,),
        )
    return _check(alpha3, validator, id_number)


def validate_many(items: Iterable[Tuple[str, str]]) -> List[ValidationResult]:
    """
    Validate several ID numbers, each with its own country.

    :param items: ``(country, id_number)`` pairs, as the arguments of :func:`validate`.
    :return: one :class:`ValidationResult` per pair, in the order of ``items``.
    """
    return [validate(country, id_number) for country, id_number in items]


def _check(alpha3: str, validator: Any, id_number: str) -> ValidationResult:
    """Validate with the ID class of a resolved country, and parse a valid ID number when the class can."""
    try:
        if not validator.validate(id_number):
            return ValidationResult(
                is_valid=False,
                country_code=alpha3,
                id_number=id_number,
                reason=FailureReason.VALIDATION_FAILED,
            )
        extracted_info = None
        if callable(getattr(validator, 'parse', None)):
            parsed = validator.parse(id_number)
            if parsed is not None:
                extracted_info = dict(parsed)
    except Exception as exc:
        return ValidationResult(
            is_valid=False,
            country_code=alpha3,
            id_number=id_number,
            reason=FailureReason.VALIDATION_FAILED,
            error_message='%s: %s' % (type(exc).__name__, exc),
        )
    return ValidationResult(is_valid=True, country_code=alpha3, id_number=id_number, extracted_info=extracted_info)
