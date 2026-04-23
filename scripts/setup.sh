#!/usr/bin/env bash
# One-shot installer for jiphyeonjeon-agent.
#
# What it does:
#   1. Confirm prerequisites (uv, claude CLI, 집현전 backend reachable)
#   2. Sync Python deps via `uv sync`
#   3. Prompt for 집현전 username/password and obtain a JWT via /api/auth/login
#      (or accept a pre-issued token via JIPHYEONJEON_TOKEN env)
#   4. Register the server with Claude Code (`claude mcp add jiphyeonjeon ...`)
#   5. Install the five `/jh:*` skills into ~/.claude/skills/
#
# Safe to re-run: each step is idempotent where possible.

set -euo pipefail

# Add common install locations to PATH so uv / claude are picked up when the
# script is invoked from a non-login shell (e.g. via a Claude Code Bash tool).
for candidate in "$HOME/.local/bin" "$HOME/.cargo/bin" "/opt/homebrew/bin" "/usr/local/bin"; do
  case ":$PATH:" in
    *":$candidate:"*) ;;
    *) [ -d "$candidate" ] && PATH="$candidate:$PATH" ;;
  esac
done
export PATH

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# Default to the hosted production endpoint so `/jh:setup` "just works"
# for end users.  Local developers running their own backend can override:
#   JIPHYEONJEON_BASE_URL=http://localhost:8000 bash scripts/setup.sh
BASE_URL="${JIPHYEONJEON_BASE_URL:-https://jiphyeonjeon.kr}"
SCOPE="${JIPHYEONJEON_SCOPE:-user}"
TIMEOUT="${JIPHYEONJEON_TIMEOUT:-90}"

log()  { printf '\033[1;34m[setup]\033[0m %s\n' "$*"; }
warn() { printf '\033[1;33m[warn ]\033[0m %s\n' "$*" >&2; }
err()  { printf '\033[1;31m[error]\033[0m %s\n' "$*" >&2; }

require_cmd() {
  local cmd="$1"
  local hint="${2:-}"
  if ! command -v "$cmd" >/dev/null 2>&1; then
    err "'$cmd' not found on PATH."
    [ -n "$hint" ] && err "  hint: $hint"
    exit 2
  fi
}

# ── Step 1: prerequisites ─────────────────────────────────────────────
log "checking prerequisites"
require_cmd uv     "install from https://docs.astral.sh/uv/"
require_cmd claude "install Claude Code first"
require_cmd curl
require_cmd python3

if ! curl -fsS "${BASE_URL}/health" >/dev/null 2>&1; then
  warn "집현전 backend not reachable at ${BASE_URL}"
  warn "  default is the hosted instance (https://jiphyeonjeon.kr) — check your network"
  warn "  local developers can run their own backend and point here:"
  warn "    JIPHYEONJEON_BASE_URL=http://localhost:8000 bash scripts/setup.sh"
  read -rp "continue anyway? [y/N] " cont
  case "$cont" in
    y|Y|yes) ;;
    *) err "aborted"; exit 1 ;;
  esac
fi

# ── Step 2: Python deps ───────────────────────────────────────────────
log "syncing Python dependencies with uv"
( cd "$REPO_ROOT" && uv sync >/dev/null )

# ── Step 3: obtain JWT ────────────────────────────────────────────────
TOKEN="${JIPHYEONJEON_TOKEN:-}"
if [ -z "$TOKEN" ]; then
  log "obtain a JWT from 집현전 — use existing credentials or leave TOKEN empty to prompt"
  read -rp "집현전 username: " JH_USER
  read -rsp "집현전 password: " JH_PASS
  printf '\n'

  resp="$(curl -fsS -X POST "${BASE_URL}/api/auth/login" \
    -H 'Content-Type: application/json' \
    -d "$(python3 -c 'import json,sys; u,p=sys.argv[1:]; print(json.dumps({"username":u,"password":p}))' "$JH_USER" "$JH_PASS")" \
    2>/dev/null || true)"

  if [ -z "$resp" ]; then
    err "login request failed — check network and credentials"
    exit 3
  fi

  TOKEN="$(printf '%s' "$resp" | python3 -c 'import json,sys; d=json.load(sys.stdin); print(d.get("access_token",""))')"

  if [ -z "$TOKEN" ]; then
    detail="$(printf '%s' "$resp" | python3 -c 'import json,sys; d=json.load(sys.stdin); print(d.get("detail","unknown"))' 2>/dev/null || echo 'unknown')"
    err "login did not return access_token — $detail"
    exit 3
  fi
  log "obtained JWT (length=${#TOKEN})"
else
  log "using JWT from JIPHYEONJEON_TOKEN env (length=${#TOKEN})"
fi

# ── Step 4: register with Claude Code ─────────────────────────────────
# Remove any prior registration so env vars get refreshed on re-run.
claude mcp remove jiphyeonjeon -s "$SCOPE" >/dev/null 2>&1 || true

log "registering Claude Code MCP server (scope=$SCOPE)"
claude mcp add jiphyeonjeon \
  --scope "$SCOPE" \
  -e JIPHYEONJEON_TOKEN="$TOKEN" \
  -e JIPHYEONJEON_BASE_URL="$BASE_URL" \
  -e JIPHYEONJEON_TIMEOUT="$TIMEOUT" \
  -- "$REPO_ROOT/.venv/bin/python" -m jiphyeonjeon_mcp >/dev/null

# ── Step 5: install skills ────────────────────────────────────────────
log "installing /jh:* skills into ~/.claude/skills"
( cd "$REPO_ROOT" && make -s install-skills >/dev/null )

# ── Done ──────────────────────────────────────────────────────────────
log "setup complete"
echo
claude mcp get jiphyeonjeon 2>/dev/null | sed -n '1,6p'
echo
log "available skills in Claude Code:"
ls -1 "$HOME/.claude/skills" | grep '^jh-' | sed 's/^/  /'
echo
log "test in a new Claude Code session:"
echo "    transformer attention 논문 3편 찾아줘    →  search_papers"
echo "    오늘 논문 브리핑 해줘                 →  /jh:daily-digest"
echo "    최근 논문 딥리뷰 해줘                  →  /jh:review-paper"
