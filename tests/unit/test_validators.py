"""Unit tests for validate_id — path traversal defense."""

from __future__ import annotations

import pytest
from mcp.shared.exceptions import McpError

from jiphyeonjeon_mcp.validators import validate_id


def test_accepts_arxiv_id() -> None:
    assert validate_id("2401.12345", field_name="paper_id") == "2401.12345"


def test_accepts_uuid_like() -> None:
    assert validate_id("abc123-def-456", field_name="bookmark_id") == "abc123-def-456"


def test_accepts_colons_dots_underscores() -> None:
    assert validate_id("ns:item_1.v2", field_name="x") == "ns:item_1.v2"


@pytest.mark.parametrize(
    "bad",
    [
        "../admin/users",
        "..",
        "a/b",
        "id with space",
        "id\nline",
        "id'quote",
        'id"quote',
        "id;drop",
        "id?q=1",
        "",
        "a" * 201,
    ],
)
def test_rejects_traversal_and_special_chars(bad: str) -> None:
    with pytest.raises(McpError) as exc_info:
        validate_id(bad, field_name="paper_id")
    assert "허용된 형식" in str(exc_info.value)


def test_rejects_non_string() -> None:
    with pytest.raises(McpError):
        validate_id(None, field_name="x")  # type: ignore[arg-type]
