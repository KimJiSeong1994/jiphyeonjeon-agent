"""Regression tests for the upstream REST/OpenAPI compatibility gate."""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any, cast

from jiphyeonjeon_mcp.openapi_contract import validate_openapi_contract

FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "upstream-openapi-contract.json"


def _fixture() -> dict[str, Any]:
    return cast(dict[str, Any], json.loads(FIXTURE.read_text(encoding="utf-8")))


def test_checked_in_openapi_fixture_matches_mcp_contract() -> None:
    assert validate_openapi_contract(_fixture()) == []


def test_contract_gate_detects_removed_operation() -> None:
    document = copy.deepcopy(_fixture())
    del document["paths"]["/api/deep-review/report/{session_id}"]["get"]

    errors = validate_openapi_contract(document)

    assert any("GET /api/deep-review/report/{session_id}" in error for error in errors)


def test_contract_gate_detects_renamed_request_field_through_ref() -> None:
    document = copy.deepcopy(_fixture())
    properties = document["components"]["schemas"]["SearchRequest"]["properties"]
    properties["limit"] = properties.pop("max_results")

    errors = validate_openapi_contract(document)

    assert any("POST /api/search" in error and "max_results" in error for error in errors)
