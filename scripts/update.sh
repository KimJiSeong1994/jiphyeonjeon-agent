#!/usr/bin/env bash
# Updater for jiphyeonjeon-agent.
#
# What it does:
#   1. Verify we are inside a jiphyeonjeon-agent clone (pyproject.toml name match)
#   2. Refuse to run with a dirty worktree (unless --force)
#   3. git fetch --tags origin
#   4. git pull --ff-only origin main   (refuses non-fast-forward — RCE mitigation)
#   5. uv sync (frozen lockfile when present)
#   6. Reinstall skills via `make install-skills` or fallback copy
#   7. Print the resolved version and ask the user to restart Claude Code
#
# Usage:
#   bash scripts/update.sh                # standard update
#   bash scripts/update.sh --force        # ignore dirty worktree
#   bash scripts/update.sh --dry-run      # report what would change, no mutations
#
# Exit codes:
#   0  success
#   1  dirty worktree (use --force to override)
#   2  fast-forward refused (diverged branch / fork)
#   3  uv sync or skills install failed
#   4  not in a jiphyeonjeon-agent repo

set -euo pipefail

# Add common install locations to PATH so uv / git resolve when invoked from a
# non-login shell (mirrors scripts/setup.sh).
for candidate in "$HOME/.local/bin" "$HOME/.cargo/bin" "/opt/homebrew/bin" "/usr/local/bin"; do
  case ":$PATH:" in
    *":$candidate:"*) ;;
    *) [ -d "$candidate" ] && PATH="$candidate:$PATH" ;;
  esac
done
export PATH

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

FORCE=0
DRY_RUN=0
for arg in "$@"; do
  case "$arg" in
    --force)   FORCE=1 ;;
    --dry-run) DRY_RUN=1 ;;
    -h|--help)
      sed -n '2,28p' "$0"
      exit 0
      ;;
    *)
      printf '\033[1;31m[error]\033[0m unknown flag: %s\n' "$arg" >&2
      exit 64
      ;;
  esac
done

log()  { printf '\033[1;34m[update]\033[0m %s\n' "$*"; }
warn() { printf '\033[1;33m[warn  ]\033[0m %s\n' "$*" >&2; }
err()  { printf '\033[1;31m[error]\033[0m %s\n' "$*" >&2; }
ok()   { printf '\033[1;32m[ok    ]\033[0m %s\n' "$*"; }

require_cmd() {
  local cmd="$1"
  if ! command -v "$cmd" >/dev/null 2>&1; then
    err "'$cmd' not found on PATH."
    exit 3
  fi
}

# Read [project].<field> from pyproject.toml. Prefers the repo's own venv
# (Python 3.12, has tomllib); falls back to a tomli installation hint.
_read_pyproject_field() {
  local pyproject="$1"
  local field="$2"
  local py
  if [ -x "$REPO_ROOT/.venv/bin/python" ]; then
    py="$REPO_ROOT/.venv/bin/python"
  elif command -v python3.12 >/dev/null 2>&1; then
    py="python3.12"
  elif command -v python3.11 >/dev/null 2>&1; then
    py="python3.11"
  else
    py="python3"
  fi
  "$py" -c '
import sys
try:
    import tomllib
except ModuleNotFoundError:
    sys.stderr.write("error: tomllib unavailable; run `uv sync` first or install Python 3.11+\n")
    sys.exit(3)
with open(sys.argv[1], "rb") as fh:
    data = tomllib.load(fh)
print(data["project"][sys.argv[2]])
' "$pyproject" "$field"
}

# ── Step 0: prerequisites ─────────────────────────────────────────────
require_cmd git
require_cmd uv
require_cmd python3

# ── Step 1: confirm we are in a jiphyeonjeon-agent clone ──────────────
PYPROJECT="$REPO_ROOT/pyproject.toml"
if [ ! -f "$PYPROJECT" ]; then
  err "pyproject.toml not found at $PYPROJECT — is this a jiphyeonjeon-agent clone?"
  exit 4
fi

PROJECT_NAME="$(_read_pyproject_field "$PYPROJECT" name)"
if [ "$PROJECT_NAME" != "jiphyeonjeon-mcp" ]; then
  err "pyproject.toml [project].name is '$PROJECT_NAME', expected 'jiphyeonjeon-mcp'."
  err "  refusing to update: this script only knows how to update jiphyeonjeon-agent."
  exit 4
fi

cd "$REPO_ROOT"

# ── Step 2: dirty worktree check ──────────────────────────────────────
DIRTY="$(git status --porcelain)"
if [ -n "$DIRTY" ]; then
  if [ "$FORCE" -eq 0 ]; then
    err "worktree has uncommitted changes:"
    printf '%s\n' "$DIRTY" | sed 's/^/    /' >&2
    err "commit/stash them first, or pass --force to update anyway"
    exit 1
  else
    warn "--force passed: continuing despite dirty worktree"
  fi
fi

CURRENT_BRANCH="$(git rev-parse --abbrev-ref HEAD)"
CURRENT_HEAD="$(git rev-parse --short HEAD)"

# ── Step 3: fetch + dry-run preview ───────────────────────────────────
log "fetching tags + main from origin"
if [ "$DRY_RUN" -eq 1 ]; then
  log "[dry-run] would: git fetch --tags origin"
  log "[dry-run] would: git pull --ff-only origin main"
  log "[dry-run] would: uv sync"
  log "[dry-run] would: install skills"
  log "[dry-run] current HEAD=$CURRENT_HEAD branch=$CURRENT_BRANCH"
  exit 0
fi

git fetch --tags origin

# ── Step 4: fast-forward only pull (RCE mitigation) ───────────────────
log "pulling fast-forward only from origin/main"
if ! git pull --ff-only origin main; then
  err "non-fast-forward pull refused."
  err "  current branch: $CURRENT_BRANCH (HEAD=$CURRENT_HEAD)"
  err "  rollback hint: git checkout main && git reset --hard origin/main"
  err "  if you are on a fork/feature branch, rebase or merge manually before retrying."
  exit 2
fi

# ── Step 5: sync deps ─────────────────────────────────────────────────
log "syncing Python dependencies with uv"
if [ -f "$REPO_ROOT/uv.lock" ]; then
  if ! uv sync --frozen; then
    err "uv sync --frozen failed (lockfile drift?). retry without --frozen with: uv sync"
    exit 3
  fi
else
  if ! uv sync; then
    err "uv sync failed."
    exit 3
  fi
fi

# ── Step 6: reinstall skills ──────────────────────────────────────────
log "reinstalling /jh:* skills into ~/.claude/skills"
if make -n install-skills >/dev/null 2>&1; then
  if ! make -s install-skills >/dev/null; then
    err "make install-skills failed."
    exit 3
  fi
else
  warn "Makefile target install-skills not found — falling back to direct copy"
  mkdir -p "$HOME/.claude/skills"
  for f in "$REPO_ROOT"/skills/*.md; do
    name="$(basename "$f" .md)"
    target="$HOME/.claude/skills/$name"
    mkdir -p "$target"
    cp "$f" "$target/SKILL.md"
  done
fi

# ── Done ──────────────────────────────────────────────────────────────
NEW_VERSION="$(_read_pyproject_field "$PYPROJECT" version)"
NEW_HEAD="$(git rev-parse --short HEAD)"
ok "jiphyeonjeon-agent updated to v${NEW_VERSION} (HEAD ${CURRENT_HEAD} → ${NEW_HEAD}). Restart Claude Code to apply."
