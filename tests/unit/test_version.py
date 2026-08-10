"""Verify __version__ is sourced from pyproject.toml metadata, not a literal."""

from __future__ import annotations

import json
import tomllib
from pathlib import Path

from pydantic import SecretStr

import jiphyeonjeon_mcp
from jiphyeonjeon_mcp.capability import ServerCapabilities
from jiphyeonjeon_mcp.config import Settings
from jiphyeonjeon_mcp.server import _build_server


def _pyproject_version() -> str:
    """Read [project].version from the repo's pyproject.toml."""
    root = Path(__file__).resolve().parents[2]
    with (root / "pyproject.toml").open("rb") as fh:
        data = tomllib.load(fh)
    return str(data["project"]["version"])


def test_version_matches_pyproject() -> None:
    """__version__ must match pyproject.toml [project].version exactly.

    This guards against the historical drift bug where __init__.py held
    a hardcoded literal that lagged behind pyproject.toml on release.
    """
    assert jiphyeonjeon_mcp.__version__ == _pyproject_version()


def test_mcp_server_info_uses_package_version() -> None:
    settings = Settings(token=SecretStr("tok"), auto_update_check=False)
    mcp, _registered = _build_server(
        settings,
        ServerCapabilities(version="test", capabilities=frozenset()),
    )
    assert mcp._mcp_server.version == jiphyeonjeon_mcp.__version__


def test_only_reference_registry_manifest_exists_until_mcpb_is_published() -> None:
    root = Path(__file__).resolve().parents[2]
    assert not (root / "server.json").exists()
    reference = json.loads(
        (root / "docs" / "distribution" / "server.pypi-reference.json").read_text(encoding="utf-8")
    )
    assert reference["version"] == _pyproject_version()
    assert reference["packages"][0]["version"] == _pyproject_version()
