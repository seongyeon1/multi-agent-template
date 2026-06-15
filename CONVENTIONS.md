# 컨벤션 (multi-agent 모노레포)

모든 에이전트가 따르는 규약. 도구가 강제하는 항목은 **[강제]**, 사람이 지키는 항목은 **[규율]** 로 표시.

---

## 1. 레이아웃 & 격리

```
<repo>/
  common/                # 공유 패키지 agent_common — 모든 에이전트가 의존
  agents/<slug>/         # 에이전트별 격리 디렉토리 (src 레이아웃)
    src/<slug>_agent/
      settings.py        # <SLUG>_AGENT_ prefix 전용
      domain/            # 순수
      application/       # use-case (토글 분기는 여기서 1회)
      api/               # transport (FastAPI) — 얇게
```

- **[강제]** `agents.* → common` 허용, `common → agents.*` 금지, `agents.<a> → agents.<b>` 금지. (import-linter independence/forbidden 계약)
- **[규율]** 한 커밋/MR 은 **하나의 에이전트** 또는 **common** 만 건드린다. common 변경은 영향받는 전 에이전트 CI green 으로 증명.

## 2. 환경변수 [강제]

- **에이전트 고유** → `<NAME>_AGENT_<KEY>` (예 `TAX_AGENT_API_PORT`).
- **공통 인프라** → 안정 prefix 유지: `LLM_GW_` `OCR_` `S3_` `REDIS_` `PII_` `BRAIN_PARSER_` `SLLM_` `SCZ_OAUTH_` + 플랫폼값 `ENVIRONMENT` `LOG_FORMAT` `ALLOWED_ORIGINS`.
- **`os.getenv` 직접 호출 금지** — 모든 접근은 `agent_common.settings` 경유. (`scripts/lint_env_prefix.py` 가 강제)
- `.env` 분리: 루트 `.env.common.example` + `agents/<x>/.env.agent.example`. 실제 `.env`/시크릿은 미커밋.
- 구→신 prefix 이행은 `env_with_alias(new, old)` 로 무중단 (구 이름 사용 시 DeprecationWarning).

## 3. 토글링 [규율]

- 새 동작은 **항상 토글 뒤에**, 기본 **opt-in(off)**. 배포해도 기존 동작 불변, 운영자가 env 로 점진 개방.
- 토글은 `settings` 의 typed flag 로만 노출. 호출부에서 `os.getenv` 분기 금지.
- 토글 평가는 **application 경계에서 1회** — 졸업(제거) 시 분기 한 곳만 지운다.

## 4. 주석 [규율]

- 모든 모듈 최상단 docstring 은 **"왜"** 를 설명한다 (무엇 < 배경/함정/결정).
- 비자명한 분기·우회·매직넘버엔 인라인 "왜" 주석.
- env/토글 정의엔 기본값과 opt-in 여부를 주석에 명시.

## 5. 커밋 & MR [강제]

- **Conventional Commits**: `type(scope): 한글 요약`.
  - type ∈ `feat|fix|refactor|chore|docs|test|perf|build|ci|style|revert`
  - **scope 필수** = 건드린 영역 (에이전트 slug 또는 `common`/`ci`). 예: `refactor(tax-agent): …`, `feat(common): …`
- **AI 흔적 라인 금지** (`Co-Authored-By: …Claude`, `🤖`, `Generated with`). (`scripts/check_commit_msg.py` 가 강제)
- MR 은 `.gitlab/merge_request_templates/default.md` 체크리스트를 채운다.
- **[규율]** 배포 트리에 tests/docs/scripts/notebooks/data 미포함.

## 6. 도메인 아티팩트 보호 [규율]

- `rule_*.json`·규정 프롬프트 등 **도메인 전문가 소유 자산은 엔지니어가 임의 수정하지 않는다**. 정리/이관은 제안 항목으로만 분리.

## 7. 린트/CI [강제]

| 게이트 | 로컬(pre-commit) | CI |
|--------|------------------|----|
| ruff (lint+format) | ✓ | ✓ |
| env 규약 (`lint_env_prefix.py`) | ✓ | ✓ |
| 격리 계약 (`lint-imports`) | ✓ | ✓ |
| commit-msg 규약 | ✓ (commit-msg) | — |
| 에이전트 테스트 | — | ✓ (rules:changes 스코핑) |
| mypy | — | ✓ (allow-failure) |
