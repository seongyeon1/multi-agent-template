"""LLM 게이트웨이 클라이언트 (공통 인프라 stub).

왜 stub 인가: 본 템플릿은 도메인 중립 골격이다. 실제 게이트웨이는 이 템플릿을
상속한 인스턴스가 이 자리를 구체 구현으로 채운다.
구성값은 :class:`agent_common.settings.CommonSettings` 의 ``llm_*`` 에서 읽는다.

토글 예시: 새 모델 라우팅은 ``LLM_*`` 공통 토글 뒤에 두고 기본 off 로 둔다.
"""

from __future__ import annotations

from agent_common.settings import get_common


class GatewayClient:
    """공통 게이트웨이 클라이언트 자리표시자.

    이 stub 은 구성만 들고 있고 실제 호출은 하지 않는다. 구체 구현(httpx 세션,
    재시도, 스트리밍 등)은 상속 인스턴스에서 주입한다.
    """

    def __init__(self) -> None:
        common = get_common()
        self.base_url = common.llm_base_url
        self.verify_ssl = common.llm_verify_ssl

    def is_configured(self) -> bool:
        return self.base_url is not None
