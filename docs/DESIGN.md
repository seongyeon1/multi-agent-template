# 설계: multi-agent 모노레포 하네스

> 본 문서는 `tax_agent-phase-a` 하네스에서 추출한 컨벤션을 재사용 가능한 모노레포
> 골격으로 정리한 설계 근거다. 산출물 계보: `multi-agent-template`(generic, 본 repo)
> → `skt-agent-template`(SKT 구체화) → `scz-sys`(실 모노레포).

## 1. 문제

여러 에이전트(tax/medical/icms/…)를 한 모노레포(`scz-sys`)에서 개발한다. 두 요구가 충돌한다:

1. **공통 코드 공유** — 게이트웨이/스토리지/PII/로깅/설정을 중복 없이.
2. **에이전트 간 무영향** — 한 에이전트 커밋이 다른 에이전트에 영향을 주면 안 됨.

공유 `common/` 은 본질적 결합점이라 둘은 그냥은 양립하지 않는다.

## 2. 해법 — 경계를 둘로 가른다

- **agent ↔ agent: 하드 격리.** 서로 import 금지(import-linter independence), CI 도 한쪽
  변경 시 다른 쪽을 돌리지 않음(`rules:changes`), CODEOWNERS 로 리뷰 분리.
- **common → agents: 명시적·가시화된 결합.** `common/**` 변경은 전 에이전트 CI 를
  강제 재실행 → "이건 모두에게 영향"임을 숨기지 않고 드러낸다. common 은 가산적·하위호환
  규율, 깨는 변경은 전 에이전트를 한 MR 에서 같이 고쳐 green 으로 증명.

## 3. 환경변수

- 두 네임스페이스: 에이전트 고유 `<NAME>_AGENT_*`, 공통 인프라 안정 prefix.
- 중앙 로더 `agent_common.settings` — 흩어진 `os.getenv`(구 코드 30여 파일)를 수렴.
  `os.getenv` 직접 호출은 settings.py 외 금지(린트 강제).
- 구→신 prefix 이행은 `env_with_alias` 로 무중단. (예: `TAXAGENT_*` → `TAX_AGENT_*`)

## 4. 토글

- 새 동작은 토글(기본 off) 뒤에. application 경계에서 1회 평가. typed flag 로만 노출.

## 5. 강제 수단

| 규약 | 강제 도구 |
|------|-----------|
| 격리(agent↔agent, common→agent) | import-linter 계약 + CI rules:changes |
| env prefix / os.getenv 금지 | `scripts/lint_env_prefix.py` (pre-commit + CI) |
| 커밋 규약 + AI 흔적 차단 | `scripts/check_commit_msg.py` (commit-msg 훅) |
| 코드 스타일 | ruff (lint+format) |
| 리뷰 라우팅 | CODEOWNERS |

## 6. 비목표 (YAGNI)

- 에이전트별 별도 repo: 채택 안 함(모노레포 + 디렉토리 격리로 충분).
- common 버전 pin/패키지 배포: 초기엔 editable 단일 트리. 필요 시 후속.
- GitHub Actions 정본화: CI 정본은 GitLab. GH 액션은 본 템플릿 repo green 유지용 최소.
