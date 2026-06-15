"""application — use-case 계층. 토글 분기의 모범 위치.

토글(`new_parser_enabled`)을 여기서 한 번만 읽어 분기하고, 그 아래는 토글을
모르는 순수 함수로 둔다. 이렇게 하면 토글 제거(졸업) 시 분기 한 곳만 지우면 된다.
"""
from __future__ import annotations

from example_agent.domain import ParseResult
from example_agent.settings import get_settings


def parse_document(raw: str) -> ParseResult:
    """문서 파싱 진입점. 토글에 따라 신/구 파서 선택.

    규약: 토글은 application 경계에서 1회 평가. 신규 경로는 기본 off 라
    배포해도 기존 동작이 그대로 유지되고, 운영자가 env 로 점진 개방한다.
    """
    settings = get_settings()
    if settings.new_parser_enabled:
        return _parse_new(raw)
    return _parse_legacy(raw)


def _parse_legacy(raw: str) -> ParseResult:
    return ParseResult(text=raw.strip(), parser="legacy")


def _parse_new(raw: str) -> ParseResult:
    # 신규 파서 예시 — 공백 정규화까지 수행(동작 차이를 토글로 격리).
    return ParseResult(text=" ".join(raw.split()), parser="new")
