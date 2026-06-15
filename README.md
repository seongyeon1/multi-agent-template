# multi-agent-template

여러 AI 에이전트를 **하나의 모노레포**에서 개발하면서, **공통 모듈은 공유**하되
**에이전트끼리는 격리**(한쪽 변경이 다른 쪽에 영향 X)하는 재사용 가능한 골격.

도메인 중립 템플릿입니다. 조직 특화(게이트웨이/스토리지 구체 구현, 사내 CI)는
이 템플릿을 상속한 인스턴스(예: `skt-agent-template`)에서 채웁니다.

## 핵심 아이디어

| 목표 | 장치 |
|------|------|
| 공통 코드 공유 | `common/` (`agent_common` 패키지) — 모든 에이전트가 의존 |
| 에이전트 간 격리 | import-linter independence 계약 + CI `rules:changes` 스코핑 + CODEOWNERS |
| 공유 변경 가시화 | `common/**` 변경 시 전 에이전트 CI 재실행 |
| 환경변수 규율 | `<NAME>_AGENT_` prefix + 공통 prefix, 중앙 `settings`, `os.getenv` 금지 |
| 점진 배포 | 토글(기본 off) 규약 |
| 일관된 협업 | Conventional Commits + scope, pre-commit, MR 템플릿 |

자세한 규약은 [CONVENTIONS.md](CONVENTIONS.md), 설계 근거는 [docs/DESIGN.md](docs/DESIGN.md).

## 빠른 시작

```bash
make install        # common + 예시 에이전트 editable 설치 + 도구
make hooks          # pre-commit 훅 등록 (commit-msg 포함)
make lint           # ruff + env 규약 + 격리 계약
make test           # 전체 테스트

make new-agent NAME=tax     # agents/tax/ 스캐폴드 (TAX_AGENT_ prefix)
```

## 디렉토리

```
common/                       공유 하네스 (settings/logging/gateway/storage/pii)
agents/_example/              기준 에이전트 (복제 원본)
scripts/                      new_agent · lint_env_prefix · check_commit_msg
.gitlab-ci.yml                per-agent 스코핑 CI (정본)
.github/workflows/ci.yml      이 repo 자체 green 유지용 최소 CI
.gitlab/merge_request_templates/default.md
CODEOWNERS · CONVENTIONS.md · .pre-commit-config.yaml
docs/DESIGN.md · docs/MIGRATION.md
```

## 새 에이전트 추가

1. `make new-agent NAME=<slug>` → `agents/<slug>/` 생성 (`<SLUG>_AGENT_` prefix 치환).
2. `pyproject.toml`/`import-linter` 의 `independence.modules`, `root_packages` 에 패키지명 추가.
3. `.gitlab-ci.yml` 에 `test:<slug>` 잡 추가(템플릿 복제), `CODEOWNERS` 한 줄.
4. `agents/<slug>/.env.agent.example` 채우기.
