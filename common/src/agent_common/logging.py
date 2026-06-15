"""공통 로깅 설정 — 에이전트 간 동일한 포맷/레벨 규약.

``LOG_FORMAT=json`` 이면 구조화 로그(운영), 그 외엔 사람이 읽는 text(로컬).
에이전트는 기동 시 :func:`configure_logging` 한 번만 부르면 된다.
"""

from __future__ import annotations

import logging
import sys

from agent_common.settings import get_common

_TEXT_FMT = "%(asctime)s %(levelname)-7s %(name)s — %(message)s"


def configure_logging(level: int = logging.INFO) -> None:
    """루트 로거를 공통 규약으로 1회 구성(멱등)."""
    common = get_common()
    handler = logging.StreamHandler(sys.stdout)
    if common.log_format.lower() == "json":
        # 운영: 한 줄 = 한 JSON. 외부 의존 없이 최소 구현(실 배포 시 교체 가능).
        handler.setFormatter(_JsonFormatter())
    else:
        handler.setFormatter(logging.Formatter(_TEXT_FMT))
    root = logging.getLogger()
    root.handlers[:] = [handler]  # 중복 핸들러 방지(멱등)
    root.setLevel(level)


class _JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        import json

        payload = {
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }
        if record.exc_info:
            payload["exc"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)
