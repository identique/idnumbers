"""
Unified validation and parsing of the primary ID number of any supported country.

:func:`validate` takes the code of a country and an ID number, and returns a :class:`ValidationResult` that says
whether the ID number is valid, which country was used, what the ID number contains and why it failed. It never
raises: an unknown country, a malformed ID number and an unexpected error inside a validator all give a result with
``is_valid`` set to ``False``. The country is found with :func:`idnumbers.registry.resolve_country`, so an alpha-2
or alpha-3 code in any letter case works. The ID number is validated exactly as given, without any normalization.

:func:`parse_id_info` uses the same validation path and returns a discriminated parsing result.

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
    result.reason               # <FailureReason.CHECKSUM_MISMATCH: 'checksum_mismatch'>
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Iterable, List, Literal, Mapping, Optional, Tuple, Type, Union

from . import registry

__all__ = [
    'FailureReason', 'ValidationResult', 'ParseSuccess', 'ParseFailure', 'ParseIdInfoResult',
    'validate', 'validate_many', 'parse_id_info', 'failure_reason',
]


class FailureReason(str, Enum):
    """
    Why the validation of an ID number failed.

    The set of reasons is not exhaustive: later releases may add values, so don't match it exhaustively.
    """

    UNSUPPORTED_COUNTRY = 'unsupported_country'
    """The country code is unknown, or it isn't a ``str``."""

    INVALID_LENGTH = 'invalid_length'
    """The ID number has a length the ID type doesn't allow."""

    INVALID_FORMAT = 'invalid_format'
    """The ID number doesn't have the format of the ID type."""

    CHECKSUM_MISMATCH = 'checksum_mismatch'
    """The check digit or check characters are wrong."""

    INVALID_BIRTHDATE = 'invalid_birthdate'
    """The birth date inside the ID number isn't a real date."""

    VALIDATION_FAILED = 'validation_failed'
    """The validator rejected the ID number without a more precise reason, or it raised an exception."""

    NOT_PARSABLE = 'not_parsable'
    """A valid ID has no extractable information, including when its type has no parser.

    Only :func:`parse_id_info` produces this reason.
    """


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


@dataclass(frozen=True)
class ParseSuccess:
    """Parsed information from a valid primary ID. Fields are frozen; ``info`` is a fresh, shallow dictionary."""

    country_code: str
    """The resolved ISO 3166-1 alpha-3 code."""

    id_number: str
    """The ID number exactly as it was passed in."""

    info: Mapping[str, Any]
    """The country class's parsed fields, without conversion of dates, enums or other values."""

    ok: Literal[True] = True
    """The discriminator for successful parsing."""


@dataclass(frozen=True)
class ParseFailure:
    """An unsupported country, invalid ID, unparseable valid ID or validator/parser exception."""

    country_code: Optional[str]
    """The resolved alpha-3 code, or ``None`` for an unsupported country."""

    id_number: str
    """The ID number exactly as it was passed in."""

    reason: FailureReason
    """Why no parsed information is available."""

    error_message: Optional[str] = None
    """Unsupported-country or exception detail, with the same formatting as :func:`validate`."""

    ok: Literal[False] = False
    """The discriminator for unsuccessful parsing."""


ParseIdInfoResult = Union[ParseSuccess, ParseFailure]
"""The discriminated result of :func:`parse_id_info`; narrow with ``result.ok`` or ``isinstance``."""


def parse_id_info(country: str, id_number: str) -> ParseIdInfoResult:
    """
    Validate and parse the primary ``NationalID`` of a country, without normalizing the input.

    Country lookup and validation failures match :func:`validate`. A valid ID whose class has no parser, or whose
    parser returns ``None``, gives :attr:`FailureReason.NOT_PARSABLE`. Validator/parser exceptions give
    :attr:`FailureReason.VALIDATION_FAILED` with their detail in ``error_message``. This function never raises.
    Country-specific ``parse()`` methods are unchanged; secondary ID types are not selected by this entry point.

    :param country: an alpha-2 or alpha-3 code, or a registered alias, in any letter case.
    :param id_number: the ID number exactly as supplied.
    :return: a frozen :class:`ParseSuccess` with a fresh dictionary of parsed fields, or a :class:`ParseFailure`.
    """
    result = validate(country, id_number)
    if not result.is_valid:
        # validate() always supplies a reason on failure.
        assert result.reason is not None
        return ParseFailure(result.country_code, result.id_number, result.reason, result.error_message)
    if result.extracted_info is None:
        return ParseFailure(result.country_code, result.id_number, FailureReason.NOT_PARSABLE)
    # Successful validation always resolves the country; _check() already copied the parsed dictionary.
    assert result.country_code is not None
    return ParseSuccess(result.country_code, result.id_number, result.extracted_info)


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
    # A supported validator has already been selected: this local import leaves package imports
    # and unsupported-country lookups lazy. Nested unified calls must not contaminate a caller's trace.
    from .nationalid import util

    token = util._birth_date_trace.set(None)
    try:
        return _check_validator(alpha3, validator, id_number)
    finally:
        util._birth_date_trace.reset(token)


def _check_validator(alpha3: str, validator: Any, id_number: str) -> ValidationResult:
    """Validate with the ID class of a resolved country, and parse a valid ID number when the class can."""
    try:
        if not validator.validate(id_number):
            return ValidationResult(
                is_valid=False,
                country_code=alpha3,
                id_number=id_number,
                reason=_derive_failure_reason(validator, id_number),
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


def failure_reason(id_class: Type[Any], id_number: str) -> Optional[FailureReason]:
    """Explain a rejected ID, including secondary types; return None for a valid ID. Never raises.

    Reasons are best effort, not a replacement for validation. Candidates preserve the input and remove whitespace
    and ``. - / ( )`` for diagnosis only. Format, definite checksum mismatch, and traced calendar failure are checked
    in that order; inconclusive checks and exceptions give :attr:`FailureReason.VALIDATION_FAILED`.
    """
    # A nested diagnostic's first validation must not contaminate its caller's trace.
    from .nationalid import util

    token = util._birth_date_trace.set(None)
    try:
        try:
            if id_class.validate(id_number):
                return None
        except Exception:
            return FailureReason.VALIDATION_FAILED
        return _derive_failure_reason(id_class, id_number)
    finally:
        util._birth_date_trace.reset(token)


def _derive_failure_reason(id_class: Type[Any], id_number: str) -> FailureReason:
    if not isinstance(id_number, str):
        return FailureReason.INVALID_FORMAT
    try:
        # Keep importing the package and unsupported-country lookup free of country-module imports.
        from .nationalid import util

        stripped = ''.join(char for char in id_number if not char.isspace() and char not in '.-/()')
        candidates = list(dict.fromkeys((id_number, stripped)))
        metadata = id_class.METADATA
        matches = [(candidate, util.match_regexp(candidate, metadata.regexp)) for candidate in candidates]
        matching = [(candidate, match) for candidate, match in matches if match is not None]
        if not matching:
            if not any(metadata.min_length <= len(candidate) <= metadata.max_length for candidate in candidates):
                return FailureReason.INVALID_LENGTH
            return FailureReason.INVALID_FORMAT
        checksum = getattr(id_class, 'checksum', None)
        if callable(checksum):
            mismatches = []
            for candidate, match in matching:
                try:
                    computed = checksum(candidate)
                    group = match.groupdict().get('checksum')
                    mismatches.append(computed is False or (
                        computed is not None and not isinstance(computed, bool)
                        and group is not None and str(computed) != group
                    ))
                except Exception:
                    mismatches.append(False)
            if all(mismatches):
                return FailureReason.CHECKSUM_MISMATCH
        token = util._birth_date_trace.set(False)
        try:
            for candidate, _ in matching:
                id_class.validate(candidate)
            if util._birth_date_trace.get():
                return FailureReason.INVALID_BIRTHDATE
        finally:
            util._birth_date_trace.reset(token)
    except Exception:
        return FailureReason.VALIDATION_FAILED
    return FailureReason.VALIDATION_FAILED
