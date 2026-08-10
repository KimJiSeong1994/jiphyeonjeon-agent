"""Capability negotiation with 집현전.

At server startup we call ``GET /api/version`` to discover which capabilities
the backend advertises. Only tools whose required capability is present will
be registered with the MCP server — this lets a newer MCP ship ahead of the
backend without runtime surprises.

If the endpoint returns 404 (older 집현전 predating the endpoint), we log a
warning on stderr and fall back to the BASELINE set.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

import httpx
from packaging.version import InvalidVersion, Version

from jiphyeonjeon_mcp import __version__
from jiphyeonjeon_mcp.config import Settings

logger = logging.getLogger(__name__)

# Conservative, public/read-only surface used only when capability discovery is
# unavailable. Mutating and long-running tools require an explicit advertisement.
BASELINE_CAPABILITIES: frozenset[str] = frozenset({"search", "papers"})


class IncompatibleClientError(RuntimeError):
    """Raised when the backend requires a newer MCP adapter version."""


@dataclass(frozen=True)
class ServerCapabilities:
    """Capabilities returned by ``GET /api/version``."""

    version: str
    capabilities: frozenset[str]
    mcp_min_client: str = "0.1.0"

    def supports(self, capability: str) -> bool:
        return capability in self.capabilities


async def discover_capabilities(settings: Settings) -> ServerCapabilities:
    """Probe ``GET /api/version`` and return negotiated capabilities.

    Uses its own short-lived httpx client so the regular client doesn't need
    to be created before we know whether capabilities are available. Never
    raises — on any error we log and return the baseline set.
    """
    url = f"{settings.normalized_base_url}/api/version"
    try:
        async with httpx.AsyncClient(timeout=5.0, verify=settings.verify_ssl) as client:
            response = await client.get(
                url,
                headers={"Authorization": f"Bearer {settings.token.get_secret_value()}"},
            )
    except httpx.RequestError as exc:
        logger.warning(
            "capability probe failed (%s); falling back to baseline tool set.",
            type(exc).__name__,
        )
        return ServerCapabilities(version="unknown", capabilities=BASELINE_CAPABILITIES)

    if response.status_code == 404:
        logger.warning(
            "/api/version not found on backend (집현전 < MCP-aware). Using baseline tool set.",
        )
        return ServerCapabilities(version="legacy", capabilities=BASELINE_CAPABILITIES)

    if not response.is_success:
        logger.warning(
            "capability probe got HTTP %s; falling back to baseline tool set.",
            response.status_code,
        )
        return ServerCapabilities(version="unknown", capabilities=BASELINE_CAPABILITIES)

    try:
        data = response.json()
        if not isinstance(data, dict):
            raise ValueError("response is not a JSON object")
        raw_caps = data.get("capabilities")
        if not isinstance(raw_caps, list) or not all(isinstance(cap, str) for cap in raw_caps):
            raise ValueError("capabilities must be a list of strings")
        caps = frozenset(raw_caps)
        version = str(data.get("version", "unknown"))
        mcp_min = str(data.get("mcp_min_client", "0.1.0"))
    except Exception as exc:
        logger.warning(
            "capability response parse failed (%s); falling back to baseline tool set.",
            exc,
        )
        return ServerCapabilities(version="unknown", capabilities=BASELINE_CAPABILITIES)

    return ServerCapabilities(
        version=version,
        capabilities=caps,
        mcp_min_client=mcp_min,
    )


def ensure_client_compatible(
    capabilities: ServerCapabilities,
    *,
    client_version: str = __version__,
) -> None:
    """Reject a backend that requires a newer adapter than this process provides."""
    try:
        current = Version(client_version)
        required = Version(capabilities.mcp_min_client)
    except InvalidVersion as exc:
        raise IncompatibleClientError(
            "Invalid MCP compatibility version from backend: "
            f"client={client_version!r}, required={capabilities.mcp_min_client!r}"
        ) from exc
    if current < required:
        raise IncompatibleClientError(
            f"Backend {capabilities.version} requires jiphyeonjeon-mcp "
            f">={required}, but this process is {current}. Upgrade the MCP adapter."
        )
