---
name: jh-update
description: jiphyeonjeon-agent 를 최신 릴리스로 업데이트한다. `git pull --ff-only` + `uv sync` + 스킬 재설치까지 한 번에. 트리거 키워드 — "집현전 업데이트", "jiphyeonjeon update", "jh update", "최신 버전으로 올려줘", "update jiphyeonjeon-agent".
---

# /jh:update

jiphyeonjeon-agent 의 in-place 업데이트. 사용자가 "집현전 업데이트해줘" 류 요청을 하거나, MCP 시작 시 stderr 에 `[jiphyeonjeon-mcp] new release ... available` 알림이 떴을 때 이 스킬이 실행된다.

기본 흐름은 `bash <repo>/scripts/update.sh` 한 줄이지만, 사전 점검과 사후 안내가 함께 필요하므로 이 스킬이 그 래퍼 역할을 한다.

## 사전 확인

1. **현재 버전 파악**
   - 빠른 방법: 사용자가 임의의 `/jh:*` 스킬을 한 번 트리거해 stderr 로그(MCP 패널)에서 `jiphyeonjeon-mcp v0.X.Y starting` 줄을 본다.
   - 또는 다음을 실행:
     ```bash
     python3 -c 'from jiphyeonjeon_mcp import __version__; print(__version__)'
     ```
   - `0.0.0+local` 이 보이면 editable/dev 설치 — 업데이트는 동일하게 진행하면 된다.

2. **업데이터 모듈 직접 호출 (선택)**
   - 자동 알림을 못 봤거나 의심스러우면, 다음으로 GitHub 최신 릴리스를 한 번 더 확인:
     ```bash
     uv run python -c 'import asyncio; from jiphyeonjeon_mcp.updater import check_for_updates; from jiphyeonjeon_mcp.config import load_settings; print(asyncio.run(check_for_updates(load_settings())))'
     ```
   - `update_available=True` 이면 진행, `False` 이면 이미 최신이므로 스킵 안내.

3. **repo 위치 확인**
   - 사용자가 clone 한 디렉토리. `~/.claude.json` 의 MCP 등록 `command` 가 `<repo>/.venv/bin/python` 을 가리키므로, 거기서 `..` 두 번 올라간 경로가 repo root.
   - 위치를 모르면 사용자에게 직접 물어본다 — 추측해서 다른 디렉토리에서 `git pull` 을 돌리지 말 것.

## 실행 순서

1. **표준 업데이트**
   ```bash
   bash <repo>/scripts/update.sh
   ```
   - `git status --porcelain` 가 비어있어야 진행. 더러우면 스크립트가 `exit 1` 으로 막는다.
   - `git fetch --tags && git pull --ff-only origin main` — non-fast-forward 는 거부 (RCE 완화).
   - `uv sync` (uv.lock 있으면 `--frozen`).
   - `make install-skills` 또는 fallback `cp` 로 `~/.claude/skills/jh-*` 갱신.

2. **dry-run 으로 미리보기 (선택)**
   ```bash
   bash <repo>/scripts/update.sh --dry-run
   ```
   - 실제 mutation 없이 어떤 명령이 돌지만 보여준다.

3. **dirty worktree 강제 진행 (위험)**
   ```bash
   bash <repo>/scripts/update.sh --force
   ```
   - 사용자가 로컬 변경분을 의식하고 있을 때만. 가능하면 먼저 `git stash` 권장.

4. **업데이트 후**
   - 스크립트가 `[ok    ] jiphyeonjeon-agent updated to vX.Y.Z. Restart Claude Code to apply.` 를 출력.
   - **반드시 Claude Code 재시작 또는 `/mcp` reconnect** 안내. MCP 프로세스가 새 코드를 로드해야 새 버전이 활성화된다.
   - 새 스킬이 추가됐을 가능성이 있으므로 `ls ~/.claude/skills | grep ^jh-` 로 확인.

## 종료 코드

| 코드 | 의미 | 권장 조치 |
|------|------|----------|
| 0    | 성공 | Claude Code 재시작 |
| 1    | 더러운 worktree | `git stash` 후 재시도, 또는 `--force` |
| 2    | non-fast-forward | 사용자가 fork/branch 인지 확인. `git checkout main && git reset --hard origin/main` 으로 정렬 후 재시도 (위험: 로컬 커밋 삭제) |
| 3    | uv sync 또는 skills 설치 실패 | `.venv` 재생성 (`rm -rf .venv && uv sync`) |
| 4    | jiphyeonjeon-agent 가 아닌 디렉토리 | 올바른 repo 경로 확인 |

## 실패 처리

- **dirty tree 에러**: 사용자에게 변경분 보여주고, 의도된 변경이면 `git stash` 또는 `--force`. 실수면 `git restore` 권장.
- **fast-forward 거부 (exit 2)**: 보통 사용자가 로컬 커밋을 했거나 fork branch 위에 있다. 무리하게 reset 하지 말고 사용자에게 의사 확인.
- **네트워크 실패**: `git fetch` 가 실패하면 보통 corporate proxy / DNS 문제. `JIPHYEONJEON_AUTO_UPDATE_CHECK=0` 으로 startup 알림 자체를 끌 수 있음.
- **uv sync 실패**: lockfile drift. `uv sync`(without --frozen) 재시도, 그래도 안 되면 `rm -rf .venv && uv sync`.
- **Claude Code 가 새 버전을 못 잡음**: `/mcp` 명령으로 `jiphyeonjeon` 만 reconnect. 그래도 stale 이면 Claude Code 자체를 재시작.

## 멱등성 (Idempotency)

- 같은 버전에서 다시 돌려도 안전. `git pull` 은 0 commit fast-forward → no-op, `uv sync` 도 lockfile 기준 no-op, `install-skills` 는 동일 파일 덮어쓰기.
- 따라서 업데이트 알림이 다시 떠도 (예: 캐시 ETag 가 stale) 그냥 다시 실행해도 부작용 없음.

## 자동 알림과의 관계

- MCP 서버가 시작될 때마다 GitHub Releases 를 확인 (`src/jiphyeonjeon_mcp/updater.py`).
- 새 릴리스가 있으면 stderr 한 줄: `[jiphyeonjeon-mcp] new release X.Y.Z available (current A.B.C). Run /jh:update to upgrade. Release notes: <url>`
- 사용자가 이 줄을 보거나, 자연어로 "집현전 업데이트" 류를 말하면 이 스킬이 트리거.
- 자동 체크를 끄고 싶다면 `JIPHYEONJEON_AUTO_UPDATE_CHECK=0` 환경변수.

## 산출물 요약 (사용자에게 보고)

업데이트 완료 후 Claude 가 사용자에게 보고할 내용:
- 업데이트된 버전 (예: `v0.1.1 → v0.2.0`)
- HEAD 변경 (`<old-sha> → <new-sha>`)
- "Claude Code 를 재시작하거나 `/mcp` 로 reconnect 하면 새 버전이 활성화됩니다" 한 줄 안내
- 새로 추가된 `/jh:*` 스킬이 있으면 목록
