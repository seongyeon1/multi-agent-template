# example_agent 로컬 타겟. 루트 Makefile 이 에이전트별로 위임할 때도 사용.
.PHONY: install test serve

install:
	pip install -e ../../common -e ".[dev]"

test:
	pytest tests -v

# 앱 기동 — 포트는 EXAMPLE_AGENT_API_PORT (기본 8000)
serve:
	uvicorn example_agent.api.app:build_app --factory --reload
