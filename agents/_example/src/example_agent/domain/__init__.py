"""domain — 순수 도메인 모델. transport/infra/common 인프라에 의존하지 않는다."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ParseResult:
    """파싱 결과 도메인 값. 어떤 파서를 썼는지(legacy/new)를 함께 들고 다닌다."""

    text: str
    parser: str  # "legacy" | "new"
