"""Startup version check against the GitHub Releases API.

This module is intentionally narrow: ``check_for_updates`` performs a single
ETag-conditional GET to ``api.github.com/repos/.../releases/latest``, compares
the latest tag to the locally installed ``__version__`` via
``packaging.version.Version``, and returns a structured ``UpdateCheckResult``.

Hard rules (mirrored in tests):

- The check is **advisory only**. It NEVER raises — every failure path returns
  an ``UpdateCheckResult`` with ``error`` populated and ``update_available=False``.
- The ``settings.auto_update_check`` opt-out short-circuits before any HTTP call
  is made. Disabled callers pay zero network cost.
- The total time budget is 2.5s (``httpx.AsyncClient(timeout=2.5)``); the
  capability probe gates startup, not this check.
- The user's JWT must NOT appear anywhere in this module — no logging, no
  ``Authorization`` header, no ``User-Agent`` segment. The GitHub API is
  unauthenticated for public-repo reads.
- Inner code raises specific exceptions (``httpx.RequestError``,
  ``packaging.version.InvalidVersion``, ``KeyError``, ``ValueError``,
  ``json.JSONDecodeError``, ``OSError``); only the outermost wrapper catches a
  broad ``Exception`` to convert into ``UpdateCheckResult(error=...)``.
"""

from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any

import httpx
from packaging.version import InvalidVersion, Version

from jiphyeonjeon_mcp import __version__

if TYPE_CHECKING:
    from jiphyeonjeon_mcp.config import Settings

logger = logging.getLogger(__name__)

GITHUB_RELEASES_URL = (
    "https://api.github.com/repos/KimJiSeong1994/jiphyeonjeon-agent/releases/latest"
)
_TIMEOUT_SECONDS = 2.5


@dataclass(frozen=True)
class UpdateCheckResult:
    """Outcome of a single update check.

    Fields:
        current_version: The locally installed ``__version__`` (always populated).
        latest_version: The newest release tag (without ``v`` prefix) when known.
            ``None`` if the check was skipped, errored, or the server returned 304.
        update_available: True only when ``latest_version > current_version``.
        release_url: HTML URL of the latest release on GitHub, when known.
        error: Short string describing why the check did not produce an answer.
            ``None`` on a successful check (including "up to date" outcomes).
    """

    current_version: str
    latest_version: str | None = None
    update_available: bool = False
    release_url: str | None = None
    error: str | None = None


def _cache_dir() -> Path:
    """Return the directory used to persist the GitHub ETag.

    Honors ``XDG_CACHE_HOME`` (per the XDG Base Directory spec); falls back to
    ``~/.cache``. The directory is created lazily by callers.
    """
    xdg = os.environ.get("XDG_CACHE_HOME")
    base = Path(xdg) if xdg else Path.home() / ".cache"
    return base / "jiphyeonjeon-mcp"


def _etag_cache_path() -> Path:
    """Path to the JSON file that stores the last-seen ETag."""
    return _cache_dir() / "release-etag.json"


def _load_etag(current_version: str) -> str | None:
    """Return the previously stored ETag, or ``None`` if it doesn't apply.

    The cache is keyed by ``current_version`` so a downgrade (e.g. user runs
    ``git checkout v0.1.0`` after running v0.2.0) cannot produce a stale
    ``304 Not Modified`` that hides the now-relevant update notice. A version
    mismatch is treated as a cache miss.
    """
    path = _etag_cache_path()
    try:
        with path.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
    except FileNotFoundError:
        return None
    except (OSError, json.JSONDecodeError) as exc:
        # Cache corruption is recoverable: treat as no cached ETag.
        logger.debug("ignoring unreadable ETag cache at %s: %s", path, exc)
        return None
    if data.get("version") != current_version:
        # Local version changed since this ETag was captured — invalidate.
        return None
    etag = data.get("etag")
    if isinstance(etag, str) and etag:
        return etag
    return None


def _save_etag(etag: str, current_version: str) -> None:
    """Persist ``etag`` alongside ``current_version`` for next-call validation.

    Storing the version with the ETag is what makes ``_load_etag`` safe across
    local downgrades — see :func:`_load_etag` docstring. Failures are logged
    at DEBUG and swallowed; the next check will simply re-fetch the full
    payload, which is correct (just slightly slower).
    """
    path = _etag_cache_path()
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as fh:
            json.dump({"etag": etag, "version": current_version}, fh)
    except OSError as exc:
        logger.debug("could not persist ETag cache to %s: %s", path, exc)


def _parse_release_payload(payload: Any) -> tuple[Version, str]:
    """Extract ``(latest_version, release_url)`` from the GitHub JSON body.

    Raises:
        KeyError: ``tag_name`` missing.
        ValueError: ``tag_name`` not a string, or ``html_url`` not a string.
        InvalidVersion: ``tag_name`` cannot be parsed by ``packaging``.
    """
    if not isinstance(payload, dict):
        raise ValueError("GitHub response body is not a JSON object")
    tag = payload["tag_name"]
    if not isinstance(tag, str):
        raise ValueError(f"tag_name is not a string: {type(tag).__name__}")
    html_url = payload.get("html_url", "")
    if not isinstance(html_url, str):
        raise ValueError(f"html_url is not a string: {type(html_url).__name__}")
    latest = Version(tag.lstrip("v"))
    return latest, html_url


async def check_for_updates(settings: Settings) -> UpdateCheckResult:
    """Check GitHub Releases for a newer version of jiphyeonjeon-mcp.

    This function never raises. All failures are reported via
    ``UpdateCheckResult.error``.
    """
    current = __version__

    if not settings.auto_update_check:
        # Opt-out: do not touch the network, do not parse anything.
        return UpdateCheckResult(
            current_version=current,
            latest_version=None,
            update_available=False,
            release_url=None,
            error=None,
        )

    headers: dict[str, str] = {
        "Accept": "application/vnd.github+json",
        "User-Agent": f"jiphyeonjeon-mcp/{current}",
    }
    cached_etag = _load_etag(current)
    if cached_etag:
        headers["If-None-Match"] = cached_etag

    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT_SECONDS) as client:
            response = await client.get(GITHUB_RELEASES_URL, headers=headers)
    except httpx.RequestError as exc:
        return UpdateCheckResult(
            current_version=current,
            error=f"network error: {type(exc).__name__}",
        )
    except Exception as exc:  # noqa: BLE001 — outermost boundary, see module docstring
        return UpdateCheckResult(
            current_version=current,
            error=f"unexpected http failure: {type(exc).__name__}",
        )

    if response.status_code == 304:
        # Cached ETag matched: no new release. Treat as "up to date".
        return UpdateCheckResult(
            current_version=current,
            latest_version=None,
            update_available=False,
            release_url=None,
            error=None,
        )

    if not response.is_success:
        return UpdateCheckResult(
            current_version=current,
            error=f"github returned HTTP {response.status_code}",
        )

    try:
        latest, release_url = _parse_release_payload(response.json())
    except (KeyError, ValueError, InvalidVersion, json.JSONDecodeError) as exc:
        return UpdateCheckResult(
            current_version=current,
            error=f"could not parse release: {exc}",
        )
    except Exception as exc:  # noqa: BLE001 — outermost boundary, see module docstring
        return UpdateCheckResult(
            current_version=current,
            error=f"unexpected parse failure: {type(exc).__name__}",
        )

    # Persist ETag only when we actually have one — protects against weak/missing
    # ETag headers.
    new_etag = response.headers.get("etag")
    if new_etag:
        _save_etag(new_etag, current)

    try:
        current_parsed = Version(current)
    except InvalidVersion as exc:
        return UpdateCheckResult(
            current_version=current,
            latest_version=str(latest),
            update_available=False,
            release_url=release_url or None,
            error=f"local version {current!r} is unparseable: {exc}",
        )

    update_available = latest > current_parsed
    return UpdateCheckResult(
        current_version=current,
        latest_version=str(latest),
        update_available=update_available,
        release_url=release_url or None,
        error=None,
    )
