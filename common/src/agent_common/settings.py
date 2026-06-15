"""중앙 환경변수/토글 로더 — 모든 에이전트가 공유하는 단일 진입점.

왜 이 모듈이 존재하는가
------------------------
리팩토링 전 코드베이스는 `os.getenv(...)` 호출이 30여 개 파일에 흩어져 있었고
(`api/app.py` 19곳, `llm/bootstrap.py` 14곳 …) 파일마다 `_env_bool` 같은 헬퍼를
복붙해 썼다. 그 결과 (1) 어떤 환경변수가 실제로 쓰이는지 한눈에 안 보이고,
(2) 기본값/타입 파싱이 호출부마다 미묘하게 달라지고, (3) prefix 규약을 강제할
지점이 없었다.

이 모듈은 그 모든 접근을 한 곳으로 수렴시킨다. **애플리케이션 코드에서
`os.getenv` 직접 호출은 금지**되며(`scripts/lint_env_prefix.py` 가 pre-commit/CI
에서 강제), 환경변수는 반드시 여기를 거친다.

두 네임스페이스
---------------
1. 공통 인프라(에이전트 간 동일 게이트웨이): 안정 prefix 유지.
   예) ``LLM_*`` ``S3_*`` ``REDIS_*`` ``PII_*`` + 플랫폼값
   ``ENVIRONMENT`` ``LOG_FORMAT`` ``ALLOWED_ORIGINS``.
   → :class:`CommonSettings` 가 담당.
2. 에이전트 고유: ``<NAME>_AGENT_<KEY>`` (예 ``EXAMPLE_AGENT_API_PORT``).
   → 각 에이전트가 :class:`AgentSettings` 를 prefix 와 함께 인스턴스화.

토글 규약
---------
새 동작은 **항상 토글 뒤에**, 기본 opt-in(off). 토글은 여기서 typed flag 로만
노출하고 호출부는 ``settings.feature_x`` 처럼 읽는다. ``os.getenv`` 직접 분기 금지.
"""

from __future__ import annotations

import os
import warnings
from typing import Final

# bool 로 해석할 truthy 토큰. 이 집합만 True, 그 외(빈 문자열 포함)는 default.
_TRUE_TOKENS: Final[frozenset[str]] = frozenset({"1", "true", "yes", "on", "y"})


# ─────────────────────────────────────────────────────────────────────────
# 원시 파서 — 타입/기본값을 한 곳에서 결정한다. (구 코드의 _env_bool 복붙 제거)
# ─────────────────────────────────────────────────────────────────────────
def env_str(name: str, default: str | None = None) -> str | None:
    """문자열 환경변수. 미설정/빈 문자열이면 ``default``."""
    raw = os.getenv(name)
    if raw is None or raw == "":
        return default
    return raw


def env_bool(name: str, default: bool = False) -> bool:
    """불리언 토글. ``1/true/yes/on/y`` (대소문자 무시)만 True."""
    raw = os.getenv(name)
    if raw is None or raw == "":
        return default
    return raw.strip().lower() in _TRUE_TOKENS


def env_int(name: str, default: int) -> int:
    """정수 환경변수. 파싱 실패 시 경고 후 ``default`` 로 폴백(기동 중단 방지)."""
    raw = os.getenv(name)
    if raw is None or raw == "":
        return default
    try:
        return int(raw.strip())
    except ValueError:
        warnings.warn(f"{name}={raw!r} 은 정수가 아님 → 기본값 {default} 사용", stacklevel=2)
        return default


def env_with_alias(name: str, alias: str, default: str | None = None) -> str | None:
    """하위호환 시프트용. 새 이름(``name``) 우선, 없으면 구 이름(``alias``) 폴백.

    이미 배포된 ``.env`` 가 구 prefix(붙임형 등)를 들고 있을 때, 새 prefix
    (``<NAME>_AGENT_*``)로 옮기는 과도기에 deploy 를 깨지 않기 위함.
    구 이름이 실제로 쓰이면 DeprecationWarning 으로 마이그레이션을 재촉한다.
    """
    new = env_str(name)
    if new is not None:
        return new
    old = env_str(alias)
    if old is not None:
        warnings.warn(
            f"환경변수 {alias} 는 deprecated — {name} 로 교체하세요.",
            DeprecationWarning,
            stacklevel=2,
        )
        return old
    return default


# ─────────────────────────────────────────────────────────────────────────
# 공통 인프라 설정 — 에이전트 간 공유. 새 에이전트는 이걸 그대로 받아 쓴다.
# ─────────────────────────────────────────────────────────────────────────
class CommonSettings:
    """공통 prefix(``LLM_`` ``S3_`` ``REDIS_`` ``PII_`` 등) 묶음.

    프로세스당 한 번만 만들어 공유한다(:func:`get_common`). 필드는 생성 시점에
    eager 로 확정 — 런타임 중 환경변수 mutate 에 의존하지 않도록(테스트/예측 가능성).
    """

    def __init__(self) -> None:
        # 플랫폼 공통값
        self.environment: str = env_str("ENVIRONMENT", "dev") or "dev"
        self.log_format: str = env_str("LOG_FORMAT", "text") or "text"
        # CORS — 쉼표구분. 빈 값이면 빈 리스트.
        raw_origins = env_str("ALLOWED_ORIGINS", "") or ""
        self.allowed_origins: list[str] = [o.strip() for o in raw_origins.split(",") if o.strip()]

        # 공통 인프라 — 구체 클라이언트는 gateway/storage/pii 서브패키지가 이 값을 읽어 구성.
        self.llm_base_url: str | None = env_str("LLM_BASE_URL")
        self.llm_verify_ssl: bool = env_bool("LLM_VERIFY_SSL", True)
        self.redis_url: str | None = env_str("REDIS_URL")
        self.s3_bucket: str | None = env_str("S3_RAW_ARCHIVE_BUCKET")
        self.s3_region: str | None = env_str("S3_RAW_ARCHIVE_REGION")
        self.s3_enabled: bool = env_bool("S3_RAW_ARCHIVE_ENABLED", False)

    @property
    def is_prod(self) -> bool:
        return self.environment.lower() in {"prod", "production"}


_common_singleton: CommonSettings | None = None


def get_common() -> CommonSettings:
    """프로세스 공유 :class:`CommonSettings` (lazy singleton)."""
    global _common_singleton
    if _common_singleton is None:
        _common_singleton = CommonSettings()
    return _common_singleton


# ─────────────────────────────────────────────────────────────────────────
# 에이전트 고유 설정 — prefix 를 주입받아 <NAME>_AGENT_<KEY> 를 읽는다.
# ─────────────────────────────────────────────────────────────────────────
class AgentSettings:
    """에이전트 고유 환경변수 접근기. 반드시 ``<NAME>_AGENT_`` prefix 로 생성.

    사용 예 (example_agent)::

        settings = AgentSettings("EXAMPLE_AGENT_")
        port = settings.int("API_PORT", 8000)      # EXAMPLE_AGENT_API_PORT
        on = settings.flag("NEW_PARSER_ENABLED")   # EXAMPLE_AGENT_NEW_PARSER_ENABLED (기본 off)

    prefix 형식은 생성자에서 검증한다 — 규약(``<NAME>_AGENT_``)을 벗어나면 즉시 실패.
    """

    def __init__(self, prefix: str) -> None:
        if not prefix.endswith("_AGENT_") or prefix != prefix.upper():
            raise ValueError(
                f"에이전트 prefix 는 대문자 '<NAME>_AGENT_' 형식이어야 합니다 (받음: {prefix!r}). "
                "예: 'ORDERS_AGENT_', 'BILLING_AGENT_', 'EXAMPLE_AGENT_'."
            )
        self.prefix = prefix
        self.common = get_common()  # 공통값은 항상 함께 노출 → 호출부는 settings 하나만 본다.

    def str(self, key: str, default: str | None = None) -> str | None:
        return env_str(self.prefix + key, default)

    def flag(self, key: str, default: bool = False) -> bool:
        """기능 토글. 규약상 기본 opt-in(off)."""
        return env_bool(self.prefix + key, default)

    def int(self, key: str, default: int) -> int:
        return env_int(self.prefix + key, default)
