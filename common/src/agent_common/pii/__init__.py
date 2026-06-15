"""PII 처리 (공통 인프라 stub).

가명화/복원 자리표시자. 구성값은 공통 ``PII_*`` prefix 에서 읽는다.
실제 암복호(예 PII_CIPHER_KEY 기반)는 상속 인스턴스가 채운다.
가명화는 ``PII_PSEUDONYMIZE`` 공통 토글 뒤에 두고 기본 off.
"""

from __future__ import annotations

from agent_common.settings import env_bool, env_str


class PiiEngine:
    def __init__(self) -> None:
        # 공통 prefix(PII_) — 에이전트 고유가 아니므로 <NAME>_AGENT_ 를 붙이지 않는다.
        self.pseudonymize = env_bool("PII_PSEUDONYMIZE", False)
        self._cipher_key = env_str("PII_CIPHER_KEY")

    def is_configured(self) -> bool:
        return not self.pseudonymize or self._cipher_key is not None
