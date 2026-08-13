"""Fixed, caller-non-addressable endpoint construction for M9-I4."""

from __future__ import annotations

import re
from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping


MAX_DECODED_BODY_BYTES = 1_048_576
_CIK = re.compile(r"^[0-9]{10}$", re.ASCII)
_ACCESSION = re.compile(r"^[0-9]{10}-[0-9]{2}-[0-9]{6}$", re.ASCII)
_DOCUMENT = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$", re.ASCII)


class EndpointError(ValueError):
    """A fixed endpoint or strict identifier failed closed."""

    code = "SEC-ENDPOINT-DENIED"


@dataclass(frozen=True, slots=True)
class EndpointSpec:
    order: int
    capability: str
    provider_id: str
    endpoint_id: str
    endpoint_template: str
    host: str
    accept_media: tuple[str, ...]


_SPECS = (
    EndpointSpec(
        0,
        "identity",
        "sec-identity",
        "sec-company-tickers-v1",
        "https://www.sec.gov/files/company_tickers.json",
        "www.sec.gov",
        ("application/json",),
    ),
    EndpointSpec(
        1,
        "submissions",
        "sec-submissions",
        "sec-submissions-by-cik-v1",
        "https://data.sec.gov/submissions/CIK{cik}.json",
        "data.sec.gov",
        ("application/json",),
    ),
    EndpointSpec(
        2,
        "filings",
        "sec-filings",
        "sec-filing-document-v1",
        "https://www.sec.gov/Archives/edgar/data/{cik}/{accession}/{document}",
        "www.sec.gov",
        ("application/xml", "text/html", "text/plain"),
    ),
    EndpointSpec(
        3,
        "companyfacts",
        "sec-xbrl",
        "sec-companyfacts-by-cik-v1",
        "https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json",
        "data.sec.gov",
        ("application/json",),
    ),
)
ENDPOINTS: Mapping[str, EndpointSpec] = MappingProxyType(
    {item.capability: item for item in _SPECS}
)


def endpoint_specs() -> tuple[EndpointSpec, ...]:
    """Return the contract-locked four-capability order."""

    return _SPECS


def normalize_identifiers(capability: str, identifiers: Mapping[str, str]) -> dict[str, str]:
    """Validate typed identifiers without accepting any caller URL surface."""

    if capability not in ENDPOINTS:
        raise EndpointError("capability is not contract locked")
    if not isinstance(identifiers, Mapping) or any(
        not isinstance(key, str) or not isinstance(value, str)
        for key, value in identifiers.items()
    ):
        raise EndpointError("identifiers must be a string mapping")
    expected = {
        "identity": frozenset(),
        "submissions": frozenset({"cik"}),
        "filings": frozenset({"cik", "accession", "document"}),
        "companyfacts": frozenset({"cik"}),
    }[capability]
    if identifiers.keys() != expected:
        raise EndpointError("identifier fields do not match capability")
    result = dict(identifiers)
    if "cik" in result and not _CIK.fullmatch(result["cik"]):
        raise EndpointError("CIK must be exactly ten ASCII digits")
    if "accession" in result and not _ACCESSION.fullmatch(result["accession"]):
        raise EndpointError("accession must use the locked hyphenated form")
    document = result.get("document")
    if document is not None:
        if (
            not _DOCUMENT.fullmatch(document)
            or "%" in document
            or ".." in document
            or document.endswith(".")
            or document.startswith(".")
        ):
            raise EndpointError("filing document basename is denied")
    return result


def construct_endpoint(capability: str, identifiers: Mapping[str, str]) -> str:
    """Construct one fixed HTTPS URL entirely from a locked template."""

    values = normalize_identifiers(capability, identifiers)
    spec = ENDPOINTS[capability]
    if capability == "identity":
        return spec.endpoint_template
    cik = str(int(values["cik"]))
    if capability in {"submissions", "companyfacts"}:
        return spec.endpoint_template.format(cik=values["cik"])
    accession_compact = values["accession"].replace("-", "")
    return spec.endpoint_template.format(
        cik=cik,
        accession=accession_compact,
        document=values["document"],
    )


def request_header_presence(*, user_agent_policy_valid: bool) -> dict[str, bool]:
    """Return presence flags only; no actual operator identity is accepted or retained."""

    if type(user_agent_policy_valid) is not bool:
        raise TypeError("user_agent_policy_valid must be a boolean")
    return {"accept": True, "host": True, "user_agent": user_agent_policy_valid}
