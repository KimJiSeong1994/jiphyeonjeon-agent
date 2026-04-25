"""Environment-driven configuration for the Jiphyeonjeon MCP server.

All settings come from environment variables prefixed with ``JIPHYEONJEON_``.
The token is wrapped in ``SecretStr`` so it never appears in ``repr``/logs.
"""

from __future__ import annotations

import sys

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration loaded from env vars.

    - ``JIPHYEONJEON_TOKEN`` *(required)* — Bearer JWT from ``POST /api/auth/login``.
    - ``JIPHYEONJEON_BASE_URL`` *(default: https://jiphyeonjeon.kr)* — 집현전 FastAPI root.
      End users hit the hosted instance by default; local developers override to
      ``http://localhost:8000`` when running their own PaperReviewAgent.
    - ``JIPHYEONJEON_TIMEOUT`` *(default: 30.0)* — per-request timeout in seconds.
    - ``JIPHYEONJEON_VERIFY_SSL`` *(default: True)* — disable only for dev w/ self-signed certs.
    """

    model_config = SettingsConfigDict(
        env_prefix="JIPHYEONJEON_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    token: SecretStr = Field(
        ...,
        description="JWT Bearer token obtained from POST /api/auth/login",
    )
    base_url: str = Field(
        default="https://jiphyeonjeon.kr",
        description="집현전 FastAPI base URL (no trailing slash)",
    )
    timeout: float = Field(
        default=30.0,
        ge=1.0,
        le=600.0,
        description="HTTP client timeout per request (seconds)",
    )
    verify_ssl: bool = Field(
        default=True,
        description="Verify TLS certificates (set False only for local dev)",
    )
    auto_update_check: bool = Field(
        default=True,
        description=(
            "Check GitHub Releases at server startup for a newer jiphyeonjeon-mcp "
            "version (set JIPHYEONJEON_AUTO_UPDATE_CHECK=0 to disable). The check "
            "is advisory only — it logs to stderr and never blocks startup."
        ),
    )

    @property
    def normalized_base_url(self) -> str:
        """Return ``base_url`` with trailing slash stripped."""
        return self.base_url.rstrip("/")


def load_settings() -> Settings:
    """Load settings, printing a clear fatal error to stderr on failure.

    Exits with status 1 if required env vars are missing — this surfaces cleanly
    in MCP host logs (Claude Code writes server stderr to its own log).
    """
    try:
        return Settings()  # type: ignore[call-arg]
    except Exception as exc:
        print(f"FATAL: jiphyeonjeon-mcp configuration error: {exc}", file=sys.stderr)
        print(
            "  Set JIPHYEONJEON_TOKEN (required) and optionally JIPHYEONJEON_BASE_URL.",
            file=sys.stderr,
        )
        sys.exit(1)
