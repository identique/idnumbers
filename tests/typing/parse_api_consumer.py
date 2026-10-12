"""Strict external-consumer checks, run by the default mypy/CI configuration."""

from typing import Any, Mapping, Optional

from idnumbers import FailureReason, ParseFailure, ParseIdInfoResult, ParseSuccess, parse_id_info, failure_reason
from idnumbers.nationalid import AUS, HKG, LKA, TUR
from idnumbers.nationalid.constant import Citizenship


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


by_discriminator(parse_id_info("tw", "A123456789"))
by_class(parse_id_info("us", "012-12-0928"))


secondary_reason: Optional[FailureReason] = failure_reason(AUS.MedicareNumber, "2123 45670 1")
print(secondary_reason)


old_nic = LKA.OldNationalID.parse("900120001V")
if old_nic is not None:
    citizenship: Optional[Citizenship] = old_nic["citizenship"]
    if citizenship is not None:
        known_citizenship: Citizenship = citizenship
        print(known_citizenship)


hkg_checksum: Optional[str] = HKG.NationalID.checksum("TP1490258")
tur_checksum: Optional[str] = TUR.NationalID.checksum("10000000146")
print(hkg_checksum, tur_checksum)
