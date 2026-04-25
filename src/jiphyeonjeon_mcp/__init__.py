"""jiphyeonjeon-mcp — MCP server wrapping 집현전 (PaperReviewAgent) REST API."""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as _pkg_version

try:
    __version__ = _pkg_version("jiphyeonjeon-mcp")
except PackageNotFoundError:
    # Fallback for editable/dev installs where metadata isn't built yet.
    __version__ = "0.0.0+local"

__all__ = ["__version__"]
