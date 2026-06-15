# 루트 Makefile — 워크스페이스 전역 타겟. 에이전트별 작업은 agents/<x>/Makefile.
.PHONY: install hooks lint lint-env lint-imports test new-agent

# common + 예시 에이전트를 editable 설치 (+ pre-commit)
install:
	pip install -e ./common -e "./common[dev]" -e "./agents/_example[dev]"
	pip install ruff import-linter pre-commit

# pre-commit 훅 등록 (commit-msg 포함)
hooks:
	pre-commit install --hook-type pre-commit --hook-type commit-msg

# 전역 lint — 규약은 항상 전체에 적용
lint:
	ruff check .
	$(MAKE) lint-env
	$(MAKE) lint-imports

lint-env:
	python scripts/lint_env_prefix.py

lint-imports:
	lint-imports

# 전체 테스트 (CI 는 rules:changes 로 스코핑하지만, 로컬은 전체)
test:
	pytest common/tests agents -q

# 새 에이전트 스캐폴드 — make new-agent NAME=tax
new-agent:
	@test -n "$(NAME)" || (echo "사용법: make new-agent NAME=<slug>"; exit 1)
	python scripts/new_agent.py $(NAME)
