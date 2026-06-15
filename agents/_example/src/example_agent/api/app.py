"""api — transport 계층(FastAPI). 얇게 유지: 요청을 application 으로 위임만.

domain/application 은 FastAPI 를 모른다(import-linter 가 강제). 여기서만 HTTP 를 안다.
"""
from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel

from agent_common.logging import configure_logging
from example_agent.application import parse_document
from example_agent.settings import get_settings


class ParseRequest(BaseModel):
    text: str


class ParseResponse(BaseModel):
    text: str
    parser: str


def build_app() -> FastAPI:
    """앱 팩토리. `uvicorn example_agent.api.app:build_app --factory` 로 기동."""
    configure_logging()
    settings = get_settings()

    app = FastAPI(title="example_agent")

    @app.get("/health")
    async def health() -> dict[str, object]:
        return {
            "status": "ok",
            "env": settings.common.environment,
            "new_parser_enabled": settings.new_parser_enabled,  # 토글 상태 가시화
        }

    @app.post("/parse", response_model=ParseResponse)
    async def parse(req: ParseRequest) -> ParseResponse:
        result = parse_document(req.text)
        return ParseResponse(text=result.text, parser=result.parser)

    return app
