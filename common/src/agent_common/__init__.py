"""agent_common — 모노레포 내 모든 에이전트가 공유하는 공통 하네스.

의존 방향 규약(import-linter 로 강제):
  agents.* → agent_common   (허용)
  agent_common → agents.*    (금지)  ← common 은 어떤 에이전트도 알지 못한다.
  agents.<a> → agents.<b>     (금지)  ← 에이전트끼리 상호 import 금지.

이 방향이 "공통 모듈은 공유하되 에이전트끼리는 격리" 를 코드 레벨에서 보장한다.
"""

from agent_common.settings import (
    AgentSettings,
    CommonSettings,
    env_bool,
    env_int,
    env_str,
    env_with_alias,
    get_common,
)

__all__ = [
    "AgentSettings",
    "CommonSettings",
    "env_bool",
    "env_int",
    "env_str",
    "env_with_alias",
    "get_common",
]
