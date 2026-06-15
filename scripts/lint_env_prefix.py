#!/usr/bin/env python3
"""env 규약 린터 — pre-commit/CI 에서 두 가지를 강제한다.

규칙 1: `os.getenv` / `os.environ[...]` 직접 호출 금지 (settings.py 밖에서).
        → 모든 환경변수 접근은 agent_common.settings 를 거쳐야 한다.
규칙 2: 에이전트 코드가 읽는 env 이름은 <NAME>_AGENT_ prefix 이거나
        승인된 공통 prefix(LLM_GW_/OCR_/S3_/REDIS_/PII_/플랫폼값) 여야 한다.

규칙 2 는 settings 헬퍼 호출 인자(문자열 리터럴)를 정적으로 훑어 검사한다.
완벽한 정적분석은 아니지만 리터럴 오타/규약이탈을 값싸게 잡는다.

사용:
    python scripts/lint_env_prefix.py <변경된 .py 파일들...>
인자가 없으면 agents/ 와 common/ 전체를 스캔.

종료코드 0 = 통과, 1 = 위반.
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# 규칙 1 면제: 중앙 로더 자신만 os.getenv 를 직접 쓸 수 있다.
GETENV_ALLOWED = {REPO_ROOT / "common" / "src" / "agent_common" / "settings.py"}

# 규칙 2 — 승인된 공통 prefix (에이전트 고유가 아닌 인프라/플랫폼값).
COMMON_PREFIXES = (
    "LLM_GW_",
    "OCR_",
    "S3_",
    "REDIS_",
    "PII_",
    "BRAIN_PARSER_",
    "SLLM_",
    "SCZ_OAUTH_",
)
COMMON_EXACT = {"ENVIRONMENT", "LOG_FORMAT", "ALLOWED_ORIGINS"}

# settings 헬퍼 — 첫 인자가 env 이름. (AgentSettings.str/flag/int 는 prefix 가
# 객체에 박혀 있으므로 여기서 검사 대상에서 제외; 생성자 prefix 검증은 런타임에.)
ENV_HELPERS = {"env_str", "env_bool", "env_int", "env_with_alias"}


def _is_agent_prefixed(name: str) -> bool:
    # <NAME>_AGENT_ — 첫 토큰이 _AGENT_ 를 포함하는 대문자 형태.
    return "_AGENT_" in name and name == name.upper()


def _is_allowed_env_name(name: str) -> bool:
    if name in COMMON_EXACT:
        return True
    if name.startswith(COMMON_PREFIXES):
        return True
    return _is_agent_prefixed(name)


def check_file(path: Path) -> list[str]:
    violations: list[str] = []
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except SyntaxError as exc:
        return [f"{path}: 파싱 실패 — {exc}"]

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func

        # 규칙 1 — os.getenv(...) / os.environ.get(...)
        if isinstance(func, ast.Attribute) and func.attr in {"getenv"}:
            if isinstance(func.value, ast.Name) and func.value.id == "os":
                if path.resolve() not in GETENV_ALLOWED:
                    violations.append(
                        f"{path}:{node.lineno}: os.getenv 직접 호출 금지 — agent_common.settings 를 거치세요."
                    )

        # 규칙 2 — settings 헬퍼의 첫 인자 리터럴 prefix 검사.
        #   테스트는 면제: 파서 자체를 임의 env 이름(X_FLAG 등)으로 검증하므로.
        fname = func.attr if isinstance(func, ast.Attribute) else getattr(func, "id", None)
        if fname in ENV_HELPERS and node.args and "tests" not in path.parts:
            first = node.args[0]
            if isinstance(first, ast.Constant) and isinstance(first.value, str):
                name = first.value
                if not _is_allowed_env_name(name):
                    violations.append(
                        f"{path}:{node.lineno}: env 이름 {name!r} 가 규약 위반 — "
                        "<NAME>_AGENT_ 또는 승인된 공통 prefix 여야 합니다."
                    )
    return violations


def _default_targets() -> list[Path]:
    targets: list[Path] = []
    for base in ("agents", "common"):
        targets.extend((REPO_ROOT / base).rglob("*.py"))
    return targets


def main(argv: list[str]) -> int:
    paths = [Path(a) for a in argv] if argv else _default_targets()
    all_violations: list[str] = []
    for p in paths:
        if p.suffix != ".py" or not p.exists():
            continue
        all_violations.extend(check_file(p))

    if all_violations:
        print("env 규약 위반:")
        for v in all_violations:
            print(f"  - {v}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
