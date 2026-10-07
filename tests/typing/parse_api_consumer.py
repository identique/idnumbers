"""Strict external-consumer checks, run by the default mypy/CI configuration."""

from typing import Any, Mapping, Optional

from idnumbers import FailureReason, ParseFailure, ParseIdInfoResult, ParseSuccess, parse_id_info


def by_discriminator(result: ParseIdInfoResult) -> None:
    if result.ok:
        success: ParseSuccess = result
        code: str = success.country_code
        info: Mapping[str, Any] = result.info
        print(code, info)
    else:
        failure: ParseFailure = result
        reason: FailureReason = result.reason
        message: Optional[str] = failure.error_message
        print(reason, message)


def by_class(result: ParseIdInfoResult) -> None:
    if isinstance(result, ParseSuccess):
        info: Mapping[str, Any] = result.info
        print(info)
    else:
        failure: ParseFailure = result
        print(failure.reason)


by_discriminator(parse_id_info('tw', 'A123456789'))
by_class(parse_id_info('us', '012-12-0928'))
