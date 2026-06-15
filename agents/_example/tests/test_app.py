"""example_agent — 토글 분기/엔드포인트 회귀 테스트.

토글 기본(off)에선 legacy, 켜면 new 파서로 가는 것을 고정한다. 설정 싱글톤을
환경변수 변경 후 리셋해야 해서 _singleton 을 직접 비운다.
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from example_agent import settings as agent_settings
from example_agent.api.app import build_app
from example_agent.application import parse_document


@pytest.fixture(autouse=True)
def _reset_settings_singleton():
    agent_settings._singleton = None
    yield
    agent_settings._singleton = None


def test_toggle_off_uses_legacy(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("EXAMPLE_AGENT_NEW_PARSER_ENABLED", raising=False)
    result = parse_document("  a   b  ")
    assert result.parser == "legacy"
    assert result.text == "a   b"  # legacy 는 strip 만


def test_toggle_on_uses_new(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("EXAMPLE_AGENT_NEW_PARSER_ENABLED", "1")
    result = parse_document("  a   b  ")
    assert result.parser == "new"
    assert result.text == "a b"  # new 는 공백 정규화


def test_health_endpoint() -> None:
    client = TestClient(build_app())
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"
