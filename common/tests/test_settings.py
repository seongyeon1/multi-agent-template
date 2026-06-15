"""agent_common.settings 회귀 테스트 — 파서/prefix 검증/하위호환 시프트."""

from __future__ import annotations

import warnings

import pytest
from agent_common import settings as S
from agent_common.settings import AgentSettings


def test_env_bool_truthy(monkeypatch: pytest.MonkeyPatch) -> None:
    for tok in ("1", "true", "TRUE", "yes", "on", "y"):
        monkeypatch.setenv("X_FLAG", tok)
        assert S.env_bool("X_FLAG") is True
    for tok in ("0", "false", "no", ""):
        monkeypatch.setenv("X_FLAG", tok)
        assert S.env_bool("X_FLAG", default=False) is False


def test_env_int_fallback_on_garbage(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("X_PORT", "not-a-number")
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        assert S.env_int("X_PORT", 8000) == 8000


def test_env_with_alias_prefers_new_and_warns_on_old(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("ORDERS_AGENT_DB_URL", raising=False)
    monkeypatch.setenv("ORDERSAGENT_DB_URL", "postgres://old")
    with pytest.warns(DeprecationWarning):
        assert S.env_with_alias("ORDERS_AGENT_DB_URL", "ORDERSAGENT_DB_URL") == "postgres://old"

    monkeypatch.setenv("ORDERS_AGENT_DB_URL", "postgres://new")
    assert S.env_with_alias("ORDERS_AGENT_DB_URL", "ORDERSAGENT_DB_URL") == "postgres://new"


def test_agent_settings_rejects_bad_prefix() -> None:
    with pytest.raises(ValueError):
        AgentSettings("orders_agent_")  # 소문자
    with pytest.raises(ValueError):
        AgentSettings("TAX_")  # _AGENT_ 없음


def test_agent_settings_reads_prefixed(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("EXAMPLE_AGENT_API_PORT", "9001")
    s = AgentSettings("EXAMPLE_AGENT_")
    assert s.int("API_PORT", 8000) == 9001
    assert s.flag("MISSING_FLAG") is False
