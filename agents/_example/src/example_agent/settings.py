"""example_agent 고유 설정 — EXAMPLE_AGENT_ prefix 전용.

새 에이전트는 `scripts/new_agent.py` 가 이 파일을 복제하며 prefix 를 치환한다
(EXAMPLE_AGENT_ → ORDERS_AGENT_ 등). 호출부는 여기 정의된 typed 필드만 읽고,
환경변수 이름이나 os.getenv 를 직접 만지지 않는다.
"""
from __future__ import annotations

from agent_common import AgentSettings

# 이 에이전트의 prefix. new_agent 스캐폴더가 이 리터럴을 치환한다.
_PREFIX = "EXAMPLE_AGENT_"


class Settings:
    """example_agent 설정 묶음. 공통값은 ``.common`` 으로 함께 노출."""

    def __init__(self) -> None:
        s = AgentSettings(_PREFIX)
        self._s = s
        self.common = s.common

        # 에이전트 고유값 — EXAMPLE_AGENT_<KEY>
        self.api_port: int = s.int("API_PORT", 8000)
        self.api_host: str = s.str("API_HOST", "127.0.0.1") or "127.0.0.1"

        # 토글 규약: 새 동작은 토글 뒤에, 기본 opt-in(off).
        # 예) 새 파서를 점진 도입 — EXAMPLE_AGENT_NEW_PARSER_ENABLED=1 일 때만 on.
        self.new_parser_enabled: bool = s.flag("NEW_PARSER_ENABLED", default=False)


_singleton: Settings | None = None


def get_settings() -> Settings:
    """프로세스 공유 설정(lazy singleton)."""
    global _singleton
    if _singleton is None:
        _singleton = Settings()
    return _singleton
