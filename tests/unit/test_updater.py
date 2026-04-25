"""Unit tests for the GitHub Releases startup update check.

The check is advisory: every failure path must return an
``UpdateCheckResult`` with ``error`` populated, never raise. ETag
persistence is exercised through a per-test ``tmp_path`` cache directory
(``XDG_CACHE_HOME``).
"""

from __future__ import annotations

import json
from collections.abc import Iterator
from pathlib import Path
from unittest.mock import patch

import httpx
import pytest
import respx
from pydantic import SecretStr

import jiphyeonjeon_mcp.updater as updater_mod
from jiphyeonjeon_mcp.config import Settings
from jiphyeonjeon_mcp.updater import (
    GITHUB_RELEASES_URL,
    UpdateCheckResult,
    check_for_updates,
)


def _settings(*, auto_update_check: bool = True) -> Settings:
    return Settings(
        token=SecretStr("tok"),
        base_url="http://backend.test",
        timeout=5.0,
        verify_ssl=True,
        auto_update_check=auto_update_check,
    )


@pytest.fixture(autouse=True)
def _isolated_cache(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[Path]:
    """Redirect XDG_CACHE_HOME to a tmp dir so ETag state never leaks across tests."""
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path))
    yield tmp_path


@pytest.fixture
def _pin_version(monkeypatch: pytest.MonkeyPatch) -> str:
    """Pin __version__ to 0.1.1 inside the updater module so tests are deterministic."""
    monkeypatch.setattr(updater_mod, "__version__", "0.1.1")
    return "0.1.1"


@respx.mock
async def test_check_disabled_returns_skipped(_pin_version: str) -> None:
    route = respx.get(GITHUB_RELEASES_URL)

    result = await check_for_updates(_settings(auto_update_check=False))

    assert result == UpdateCheckResult(
        current_version="0.1.1",
        latest_version=None,
        update_available=False,
        release_url=None,
        error=None,
    )
    assert route.call_count == 0, "no HTTP call should fire when opt-out is set"


@respx.mock
async def test_newer_release_sets_update_available(_pin_version: str) -> None:
    respx.get(GITHUB_RELEASES_URL).mock(
        return_value=httpx.Response(
            200,
            json={
                "tag_name": "v0.2.0",
                "html_url": "https://github.com/KimJiSeong1994/jiphyeonjeon-agent/releases/tag/v0.2.0",
            },
            headers={"ETag": '"abc123"'},
        )
    )

    result = await check_for_updates(_settings())

    assert result.update_available is True
    assert result.latest_version == "0.2.0"
    assert result.current_version == "0.1.1"
    assert result.release_url is not None and "v0.2.0" in result.release_url
    assert result.error is None


@respx.mock
async def test_same_version_no_update(_pin_version: str) -> None:
    respx.get(GITHUB_RELEASES_URL).mock(
        return_value=httpx.Response(
            200,
            json={
                "tag_name": "v0.1.1",
                "html_url": "https://github.com/KimJiSeong1994/jiphyeonjeon-agent/releases/tag/v0.1.1",
            },
        )
    )

    result = await check_for_updates(_settings())

    assert result.update_available is False
    assert result.latest_version == "0.1.1"
    assert result.error is None


@respx.mock
async def test_etag_304_treated_as_no_update(_pin_version: str, _isolated_cache: Path) -> None:
    # Pre-populate the ETag cache as though a previous run had stored one.
    cache_file = _isolated_cache / "jiphyeonjeon-mcp" / "release-etag.json"
    cache_file.parent.mkdir(parents=True, exist_ok=True)
    # Cache must include the matching version, otherwise _load_etag invalidates
    # it (downgrade-safety guard).  _pin_version pins to "0.1.1".
    cache_file.write_text(
        json.dumps({"etag": '"cached-etag"', "version": "0.1.1"}),
        encoding="utf-8",
    )

    route = respx.get(GITHUB_RELEASES_URL).mock(return_value=httpx.Response(304))

    result = await check_for_updates(_settings())

    assert result.update_available is False
    assert result.latest_version is None
    assert result.error is None
    # Confirm we sent the conditional header, not just got lucky with a 304.
    sent_request = route.calls.last.request
    assert sent_request.headers.get("If-None-Match") == '"cached-etag"'


async def test_network_error_returns_skipped_not_raise(_pin_version: str) -> None:
    boom = httpx.ConnectError("boom")

    with patch("jiphyeonjeon_mcp.updater.httpx.AsyncClient") as fake_client:
        # AsyncClient(...) returns an instance whose async-context-manager .get raises.
        instance = fake_client.return_value
        instance.__aenter__.return_value = instance
        instance.__aexit__.return_value = False

        async def _raise(*_args: object, **_kwargs: object) -> httpx.Response:
            raise boom

        instance.get.side_effect = _raise

        result = await check_for_updates(_settings())

    assert result.update_available is False
    assert result.latest_version is None
    assert result.error is not None
    assert "ConnectError" in result.error


@respx.mock
async def test_malformed_tag_does_not_raise(_pin_version: str) -> None:
    respx.get(GITHUB_RELEASES_URL).mock(
        return_value=httpx.Response(
            200,
            json={"tag_name": "release-build-7", "html_url": "https://example/x"},
        )
    )

    result = await check_for_updates(_settings())

    assert result.update_available is False
    assert result.error is not None
    assert "release-build-7" in result.error or "parse" in result.error.lower()


@respx.mock
async def test_etag_persisted_across_calls(_pin_version: str, _isolated_cache: Path) -> None:
    # First call: server returns ETag, no cached value yet.
    first_route = respx.get(GITHUB_RELEASES_URL).mock(
        return_value=httpx.Response(
            200,
            json={
                "tag_name": "v0.1.1",
                "html_url": "https://example.test/release",
            },
            headers={"ETag": '"persisted-etag-v1"'},
        )
    )

    first = await check_for_updates(_settings())
    assert first.error is None

    # The first call must NOT have sent If-None-Match (no cache yet).
    first_request = first_route.calls.last.request
    assert "If-None-Match" not in first_request.headers

    # Cache file should now exist with the persisted ETag.
    cache_file = _isolated_cache / "jiphyeonjeon-mcp" / "release-etag.json"
    assert cache_file.exists()
    saved = json.loads(cache_file.read_text(encoding="utf-8"))
    # Cached entry must record the version that captured it so a later
    # downgrade can invalidate it (see _load_etag docstring).
    assert saved == {"etag": '"persisted-etag-v1"', "version": "0.1.1"}

    # Second call: respx route is the same; we just inspect the outgoing header.
    second = await check_for_updates(_settings())
    assert second.error is None

    second_request = first_route.calls.last.request
    assert second_request.headers.get("If-None-Match") == '"persisted-etag-v1"'


@respx.mock
async def test_etag_invalidated_on_local_version_change(
    _pin_version: str, _isolated_cache: Path
) -> None:
    """Stale ETag from a different local version must NOT short-circuit the check.

    Reproduces the downgrade hazard: a user runs v0.2.0 (capturing an ETag for
    that release), then ``git checkout v0.1.0``.  Without invalidation the
    stale ETag would yield ``304 Not Modified`` and the user would silently
    miss the now-relevant "v0.2.0 available" notice.
    """
    cache_file = _isolated_cache / "jiphyeonjeon-mcp" / "release-etag.json"
    cache_file.parent.mkdir(parents=True, exist_ok=True)
    # ETag captured under v0.2.0 — local install pinned to 0.1.1 by fixture.
    cache_file.write_text(
        json.dumps({"etag": '"stale-from-v020"', "version": "0.2.0"}),
        encoding="utf-8",
    )

    route = respx.get(GITHUB_RELEASES_URL).mock(
        return_value=httpx.Response(
            200,
            json={"tag_name": "v0.2.0", "html_url": "https://example.test/r"},
            headers={"ETag": '"fresh-etag"'},
        )
    )

    result = await check_for_updates(_settings())

    # ETag from a different version must be ignored — no If-None-Match sent.
    sent = route.calls.last.request
    assert "If-None-Match" not in sent.headers
    # And the user MUST see the update.
    assert result.update_available is True
    assert result.latest_version == "0.2.0"


@respx.mock
async def test_user_agent_does_not_leak_jwt(_pin_version: str) -> None:
    """Hard rule: the JWT must never appear in any header or URL on this call."""
    route = respx.get(GITHUB_RELEASES_URL).mock(
        return_value=httpx.Response(
            200,
            json={"tag_name": "v0.1.1", "html_url": "https://example.test/x"},
        )
    )

    settings = Settings(
        token=SecretStr("super-secret-jwt-do-not-leak"),
        base_url="http://backend.test",
        timeout=5.0,
        verify_ssl=True,
    )

    await check_for_updates(settings)

    sent = route.calls.last.request
    assert sent.headers.get("User-Agent", "").startswith("jiphyeonjeon-mcp/")
    assert "super-secret-jwt-do-not-leak" not in sent.headers.get("User-Agent", "")
    assert "Authorization" not in sent.headers
    for value in sent.headers.values():
        assert "super-secret-jwt-do-not-leak" not in value


@respx.mock
async def test_http_error_status_returns_error(_pin_version: str) -> None:
    """A non-success, non-304 HTTP status should be reported as an error, not raised."""
    respx.get(GITHUB_RELEASES_URL).mock(return_value=httpx.Response(503))

    result = await check_for_updates(_settings())

    assert result.update_available is False
    assert result.error is not None
    assert "503" in result.error
