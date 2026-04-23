---
name: jh-setup
description: jiphyeonjeon-agent 를 현재 머신의 Claude Code 에 자동 설치·등록한다. 집현전 로그인 → JWT 발급 → Claude MCP 등록 → /jh:* 스킬 복사까지 원샷. 트리거 키워드 — "집현전 agent 설치", "집현전 연결", "jiphyeonjeon setup", "install jiphyeonjeon", "jiphyeonjeon-agent 설치".
---

# /jh:setup

jiphyeonjeon-agent 원샷 설치. 사용자가 "집현전 agent 설치해줘" 류 요청을 하면 이 스킬이 실행되어 `scripts/setup.sh` 를 호출하고 결과를 보고한다.

## 사전 확인

1. **repo 위치 확인**: 사용자가 jiphyeonjeon-agent 를 clone 한 디렉토리. 이 SKILL.md 파일이 `<repo>/skills/jh-setup.md` → `~/.claude/skills/jh-setup/SKILL.md` 경로로 복사된 뒤에는 원본 repo 위치를 스킬이 직접 알 수 없으므로, 사용자에게 `pwd` 기준 확인 요청.
2. **집현전 백엔드 도달 여부**: `setup.sh` 의 기본 대상은 프로덕션 `https://jiphyeonjeon.kr` 이다. `curl -sS https://jiphyeonjeon.kr/health` 가 200 을 주면 OK. 실패하면 네트워크/인증 문제 먼저 안내. 로컬 개발 백엔드로 붙이고 싶은 사용자만 `JIPHYEONJEON_BASE_URL=http://localhost:8000` 로 override.
3. **CLI 가용성**: `uv --version`, `claude --version` 둘 다 PATH 에 있는지 체크. 없으면 각각 [uv 설치](https://docs.astral.sh/uv/) / Claude Code 설치 안내.

## 실행 순서

1. **자격증명 수집 (사용자가 직접 터미널 실행 — 프로덕션 기본)**
   - 비밀번호는 보안상 사용자가 직접 터미널에 입력해야 하므로, 다음 명령을 제시:
     ```bash
     cd <path-to-jiphyeonjeon-agent>    # 사용자가 clone 한 위치
     bash scripts/setup.sh               # → https://jiphyeonjeon.kr 로 붙는다
     ```
   - 스킬이 Claude Code 내부에서 직접 비밀번호를 다루지 않는다.

2. **대안: 토큰이 이미 있는 경우 (웹 UI Agent Key 버튼 등으로 복사)**
   ```bash
   JIPHYEONJEON_TOKEN=<paste-jwt> bash <path-to-jiphyeonjeon-agent>/scripts/setup.sh
   ```
   username/password 프롬프트를 건너뛰고 환경변수 토큰만 사용.

3. **대안 2: 로컬 개발 백엔드로 연결 (자가 호스팅 개발자)**
   ```bash
   JIPHYEONJEON_BASE_URL=http://localhost:8000 \
     bash <path-to-jiphyeonjeon-agent>/scripts/setup.sh
   ```
   자신이 띄운 PaperReviewAgent 인스턴스로 붙는다. 일반 사용자는 이 옵션을 쓸 일이 거의 없다.

4. **대안 3: Claude 에게 직접 실행 요청**
   - 사용자가 터미널 타이핑을 싫어하면, Claude 가 `Bash` 툴로 setup.sh 를 실행.
   - 이 경우 비밀번호 프롬프트는 막히므로 `JIPHYEONJEON_TOKEN` 을 사용자에게 먼저 요구한 뒤 env 로 주입.

5. **완료 검증**
   - `claude mcp get jiphyeonjeon` → `Status: ✓ Connected` 확인.
   - `ls ~/.claude/skills | grep ^jh-` → 스킬 5-6 개 노출 확인.
   - 사용자에게 "새 Claude Code 세션을 열어 `/mcp` 또는 '논문 검색해줘' 로 동작 확인하세요" 안내.

## 실패 처리

- backend 연결 실패: `scripts/setup.sh` 가 자동 경고. 집현전 백엔드 기동 명령 안내.
- JWT 발급 401: 잘못된 username/password. 다시 입력받기.
- `claude mcp add` 실패: `claude mcp remove jiphyeonjeon -s user` 후 재시도.
- venv 경로 깨짐 (레포 이동 후): `rm -rf .venv && uv sync` 안내.

## 재설치 / 업데이트

- JWT 만료 (24h): 같은 `setup.sh` 를 다시 실행. 기존 등록은 자동 제거 후 재등록됨.
- 레포 경로 변경: `setup.sh` 가 `$REPO_ROOT` 를 자기 파일 위치 기준으로 자동 계산하므로, 스크립트 자체가 이동됐다면 경로는 저절로 맞춰짐.

## 산출물 요약 (사용자에게 보고)

설치 완료 후 Claude 가 사용자에게 보고할 내용:
- 등록된 MCP 서버 이름: `jiphyeonjeon`
- 설치된 스킬 개수 (보통 5-6 개 — review-paper, build-curriculum, daily-digest, draft-blog, explore, setup)
- 테스트 예시 프롬프트 2-3개
