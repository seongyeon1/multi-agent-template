#!/usr/bin/env python3
"""commit-msg 훅 — Conventional Commits + scope 강제 + AI 흔적 차단.

강제 규칙:
  1. 제목은 `type(scope): subject` 형식.
     - type ∈ feat|fix|refactor|chore|docs|test|perf|build|ci|style|revert
     - scope 필수. 모노레포에서 scope 는 "건드린 영역" = 에이전트 slug 또는
       common/ci/repo. (예: `refactor(tax-agent): …`, `feat(common): …`)
  2. 본문 어디에도 AI 흔적 라인 금지:
     `Co-Authored-By: ... Claude`, `🤖`, `Generated with`.

pre-commit 의 commit-msg stage 로 등록한다. 인자[1] = 커밋 메시지 파일 경로.
종료코드 0 = 통과, 1 = 거부.
"""

from __future__ import annotations

import re
import sys

# scope 는 영문 소문자/숫자/하이픈. 모노레포 컨벤션상 에이전트 slug 또는 공통 영역.
HEADER_RE = re.compile(
    r"^(feat|fix|refactor|chore|docs|test|perf|build|ci|style|revert)"
    r"\(([a-z0-9][a-z0-9\-]*)\): .+"
)

# AI 흔적 — 대소문자 무시. (사내 커밋 규약: AI 생성 흔적 라인 금지)
AI_TRACE_PATTERNS = (
    re.compile(r"co-authored-by:.*claude", re.IGNORECASE),
    re.compile(r"co-authored-by:.*\bai\b", re.IGNORECASE),
    re.compile(r"generated with", re.IGNORECASE),
    re.compile(r"🤖"),
)


def validate(message: str) -> list[str]:
    errors: list[str] = []
    lines = message.splitlines()
    # 주석(#)·빈 줄을 건너뛰고 첫 실질 라인을 헤더로.
    header = next((ln for ln in lines if ln.strip() and not ln.startswith("#")), "")

    if not HEADER_RE.match(header):
        errors.append(
            "제목이 'type(scope): subject' 규약을 따르지 않습니다.\n"
            f"    받은 제목: {header!r}\n"
            "    예: refactor(tax-agent): TAXAGENT_ env 를 TAX_AGENT_ 로 통일"
        )

    for ln in lines:
        if ln.startswith("#"):
            continue
        for pat in AI_TRACE_PATTERNS:
            if pat.search(ln):
                errors.append(f"AI 흔적 라인 금지 — 제거하세요: {ln.strip()!r}")
                break
    return errors


def main(argv: list[str]) -> int:
    if len(argv) < 1:
        print("commit-msg 파일 경로가 필요합니다.")
        return 1
    try:
        message = open(argv[0], encoding="utf-8").read()
    except OSError as exc:
        print(f"커밋 메시지 읽기 실패: {exc}")
        return 1

    errors = validate(message)
    if errors:
        print("커밋 메시지 규약 위반:")
        for e in errors:
            print(f"  - {e}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
