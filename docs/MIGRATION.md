# 마이그레이션 체크리스트 — 기존 에이전트를 본 규약으로 이관

기존 repo/디렉토리(tax/medical/icms/deep)를 모노레포 + 규약으로 옮길 때 에이전트별로 따른다.
**한 에이전트씩** 별도 MR 로 진행 — 격리 원칙대로 다른 에이전트에 영향 주지 않는다.

## A. 배치
- [ ] 코드를 `agents/<slug>/src/<slug>_agent/` 로 이동 (src 레이아웃).
- [ ] 공통 인프라(게이트웨이/스토리지/PII/로깅/설정 베이스)는 `common/agent_common` 으로 승격.
- [ ] `import-linter` `root_packages` + `independence.modules` 에 패키지명 추가.
- [ ] `.gitlab-ci.yml` 에 `test:<slug>` 잡 추가, `CODEOWNERS` 한 줄.

## B. 환경변수 (가장 손이 많이 감)
- [ ] 고유 env 를 `<NAME>_AGENT_*` 로 통일. (예: `TAXAGENT_*` → `TAX_AGENT_*`)
- [ ] 공통값(`LLM_GW_`/`OCR_`/`S3_`/`REDIS_`/`PII_` 등)은 공통 prefix 로 분리.
- [ ] 흩어진 `os.getenv` 를 `agent_common.settings` / 에이전트 `settings.py` 로 수렴.
- [ ] 이미 배포된 `.env.prod` 가 구 이름이면 `env_with_alias(new, old)` 로 폴백 — 무중단.
- [ ] `.env.common.example` + `agents/<x>/.env.agent.example` 정리.
- [ ] 매핑 표 1장 작성(구 이름 → 신 이름, 공통/고유 분류) 후 MR 에 첨부.

## C. 토글
- [ ] 분기 동작을 토글(기본 off)로 감싸고 application 경계에서 1회 평가.
- [ ] `os.getenv` 직접 분기 제거.

## D. 게이트
- [ ] `ruff check .` 통과.
- [ ] `python scripts/lint_env_prefix.py` 통과 (os.getenv 잔존 0, prefix 규격).
- [ ] `lint-imports` 통과 (다른 에이전트 import 0).
- [ ] pre-commit 설치 + commit-msg 규약 통과.
- [ ] 배포 트리에 tests/docs/scripts/notebooks/data 미포함 확인 (`git ls-files`).

## 권장 순서
1. `tax` — phase-a 가 가장 성숙하므로 기준(reference)으로 먼저 정본화.
2. `medical` → `icms` → `deep` 순으로 각각 별도 MR.
