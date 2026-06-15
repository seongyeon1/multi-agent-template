<!--
MR 제목도 Conventional Commit 규약을 따르세요: type(scope): 요약
  예) refactor(orders): 주문 검증 규칙 정리
scope = 건드린 영역 (에이전트 slug 또는 common/ci).
-->

## 무엇을 / 왜
<!-- 변경 요약과 배경(왜) 한두 줄. -->

## 영향 범위 (격리 확인)
- 건드린 에이전트/모듈: <!-- agents/tax 만 / common -->
- [ ] 한 MR 은 **하나의 에이전트** 또는 **common** 만 건드립니다 (불가피하게 섞였다면 사유 명시).
- [ ] `common/` 을 바꿨다면: 영향받는 **모든 에이전트** CI 가 green 임을 확인.

## 토글
- 추가/변경한 토글: <!-- EXAMPLE_AGENT_NEW_PARSER_ENABLED -->
- [ ] 새 동작은 토글 뒤에 있고 **기본 off(opt-in)** 입니다.

## 환경변수
- 추가/변경한 env: <!-- EXAMPLE_AGENT_API_PORT, S3_... -->
- [ ] 에이전트 고유값은 `<NAME>_AGENT_` prefix, 공통은 공통 prefix.
- [ ] `.env.*.example` 갱신, 실제 `.env`/시크릿은 미커밋.

## 테스트 증빙
<!-- 명령 + 결과 붙여넣기 -->

## 체크리스트
- [ ] `ruff check .` / `lint-imports` / `lint_env_prefix.py` 통과
- [ ] 배포 트리에 tests/docs/scripts/notebooks/data 미포함
- [ ] 커밋 메시지 `type(scope):` 규약, **AI 흔적 라인 없음**
- [ ] 도메인 아티팩트(rule_*.json·규정 프롬프트)는 임의 수정하지 않음
