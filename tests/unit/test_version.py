"""Verify __version__ is sourced from pyproject.toml metadata, not a literal."""

from __future__ import annotations

import tomllib
from pathlib import Path

import jiphyeonjeon_mcp


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
