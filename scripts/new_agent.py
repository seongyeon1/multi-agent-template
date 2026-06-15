#!/usr/bin/env python3
"""새 에이전트 스캐폴더 — `agents/_example` 를 복제해 격리된 에이전트 디렉토리 생성.

사용:
    python scripts/new_agent.py <slug>
    # 예: python scripts/new_agent.py tax  →  agents/tax/ (TAX_AGENT_ prefix)

생성물은 `agents/<slug>/` 안에만 들어가므로 다른 에이전트에 영향이 없다.
slug 는 소문자/숫자/하이픈만. 패키지명은 `<slug>_agent`, env prefix 는
`<SLUG>_AGENT_` (하이픈→언더스코어, 대문자).
"""

from __future__ import annotations

import re
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = REPO_ROOT / "agents" / "_example"

SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9\-]*$")


def _replacements(slug: str) -> dict[str, str]:
    snake = slug.replace("-", "_")
    upper = snake.upper()
    return {
        "example_agent": f"{snake}_agent",
        "EXAMPLE_AGENT_": f"{upper}_AGENT_",
        "example-agent": slug,  # pyproject name, scope 등
        "_example": slug,  # 디렉토리 라벨용 보조
    }


def _apply(text: str, repl: dict[str, str]) -> str:
    # 긴 키부터 치환해 부분일치 사고 방지.
    for key in sorted(repl, key=len, reverse=True):
        text = text.replace(key, repl[key])
    return text


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        print("사용법: python scripts/new_agent.py <slug>")
        return 1
    slug = argv[0]
    if not SLUG_RE.match(slug):
        print(f"slug 는 소문자/숫자/하이픈만 허용 (받음: {slug!r})")
        return 1

    dest = REPO_ROOT / "agents" / slug
    if dest.exists():
        print(f"이미 존재: {dest}")
        return 1

    repl = _replacements(slug)
    snake = slug.replace("-", "_")

    # 빌드 산출물은 복제하지 않는다(editable 설치 부산물이 템플릿에 남아 있어도 무시).
    skip_parts = {"__pycache__", ".egg-info"}
    # prefix 치환 대상 — 텍스트 파일. 확장자 없는 Makefile/CODEOWNERS 도 포함.
    text_suffixes = {".py", ".toml", ".md", ".example", ".cfg", ".txt", ".yaml", ".yml"}
    text_names = {"Makefile", "CODEOWNERS"}

    for src in TEMPLATE.rglob("*"):
        rel = src.relative_to(TEMPLATE)
        if any(p in skip_parts or p.endswith(".egg-info") for p in rel.parts) or src.suffix == ".pyc":
            continue
        # 경로의 example_agent 디렉토리명을 치환.
        rel_str = str(rel).replace("example_agent", f"{snake}_agent")
        target = dest / rel_str
        if src.is_dir():
            target.mkdir(parents=True, exist_ok=True)
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        is_text = src.suffix in text_suffixes or src.name in text_names or src.name.startswith(".env")
        if is_text:
            target.write_text(_apply(src.read_text(encoding="utf-8"), repl), encoding="utf-8")
        else:
            shutil.copy2(src, target)

    print(f"✓ 생성됨: agents/{slug}/  (env prefix: {snake.upper()}_AGENT_)")
    print(f"  1) ruff check --fix agents/{slug}  # 치환으로 흐트러진 import 정렬")
    print(f"  2) agents/{slug}/.env.agent.example 채우고 CODEOWNERS 에 줄 추가")
    print(f"  3) pyproject(import-linter root_packages/independence)·.gitlab-ci 에 {snake}_agent 추가")
    print("  CI 는 rules:changes 로 이 디렉토리만 자동 스코핑됩니다.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
