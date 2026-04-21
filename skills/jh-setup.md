---
name: jh-setup
description: jiphyeonjeon-agent 를 현재 머신의 Claude Code 에 자동 설치·등록한다. 집현전 로그인 → JWT 발급 → Claude MCP 등록 → /jh:* 스킬 복사까지 원샷. 트리거 키워드 — "집현전 agent 설치", "집현전 연결", "jiphyeonjeon setup", "install jiphyeonjeon", "jiphyeonjeon-agent 설치".
---

# /jh:setup

jiphyeonjeon-agent 원샷 설치. 사용자가 "집현전 agent 설치해줘" 류 요청을 하면 이 스킬이 실행되어 `scripts/setup.sh` 를 호출하고 결과를 보고한다.

## 사전 확인

1. repo 위치 확인: 기본 `/Users/jiseong/git/jiphyeonjeon-agent`. 없으면 사용자에게 경로 물어보기.
2. 집현전 백엔드 기동 여부: `curl -sS http://localhost:8000/health`. 미기동이면 "먼저 집현전 백엔드를 실행하세요" 안내 후 계속 진행 여부 질의.
3. `uv`, `claude` CLI 둘 다 PATH 에 있는지 체크.

## 실행 순서

1. **자격증명 수집**
   - 사용자에게 집현전 username 물어본다.
   - 비밀번호는 보안상 사용자가 직접 터미널에 입력해야 하므로, 터미널 명령 블록을 사용자에게 제시해서 실행시킨다:
     ```bash
     cd /Users/jiseong/git/jiphyeonjeon-agent
     bash scripts/setup.sh
     ```
   - 스킬이 Claude Code 내부에서 직접 비밀번호를 다루면 안 된다. 대신 사용자가 직접 터미널에서 `setup.sh` 를 실행하도록 안내.

2. **대안: 토큰이 이미 있는 경우**
   - 사용자가 JWT 를 이미 가지고 있으면:
     ```bash
     JIPHYEONJEON_TOKEN=<paste-jwt> bash /Users/jiseong/git/jiphyeonjeon-agent/scripts/setup.sh
     ```
   - 이렇게 하면 username/password 프롬프트를 건너뛰고 환경변수 토큰만 사용.

3. **대안 2: 대기 없이 Claude 에서 바로 실행**
   - 사용자가 터미널 타이핑을 싫어하는 경우, Claude 가 직접 `Bash` 툴로 setup.sh 를 실행. 단 비밀번호 프롬프트가 막히니 `JIPHYEONJEON_TOKEN` 을 사용자에게 먼저 요구한 뒤 env 로 주입.

4. **완료 검증**
   - `claude mcp get jiphyeonjeon` 실행해서 `Status: ✓ Connected` 확인.
   - `ls ~/.claude/skills | grep ^jh-` 로 스킬 5개 노출 확인.
   - 사용자에게 "새 Claude Code 세션을 열어 /mcp 또는 '논문 검색해줘' 로 동작 확인하세요" 안내.

## 실패 처리

- backend 연결 실패: `scripts/setup.sh` 가 자동으로 경고. 집현전 백엔드 기동 명령 안내.
- JWT 발급 401: 잘못된 username/password. 다시 입력받기.
- `claude mcp add` 실패: `claude mcp remove jiphyeonjeon -s user` 후 재시도.
- venv 경로 깨짐 (레포 이동 후): `rm -rf .venv && uv sync` 안내.

## 재설치 / 업데이트

- JWT 만료 (24h): 같은 `setup.sh` 를 다시 실행. 기존 등록은 자동 제거 후 재등록됨.
- 레포 경로 변경: `JIPHYEONJEON_REPO=/new/path bash scripts/setup.sh` — 스크립트가 `$REPO_ROOT` 를 자동 계산하므로 스크립트 위치만 정확하면 OK.

## 산출물 요약 (사용자에게 보고)

설치 완료 후 Claude 가 사용자에게 보고할 내용:
- 등록된 MCP 서버 이름: `jiphyeonjeon`
- 설치된 스킬 개수 (보통 5개 — review-paper, build-curriculum, daily-digest, draft-blog, explore)
- 테스트 예시 프롬프트 2-3개
