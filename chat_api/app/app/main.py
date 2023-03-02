import logging

import fastapi
import openai
from fastapi.responses import PlainTextResponse

from app.config import settings


logger = logging.getLogger(settings.logger_name)


def create_app():
    app = fastapi.FastAPI(
        title=settings.app_name,
    )

    @app.on_event("startup")
    async def on_event_startup():
        openai.organization = settings.openai_organization
        openai.api_key = settings.openai_api_key

    @app.get("/")
    async def root():
        return PlainTextResponse("OK")

    # Router
    from app.api.router import router as router_main
    from app.api.v1.router import router as router_v1

    app.include_router(router_main, prefix=f"/api")
    app.include_router(router_v1, prefix=f"/api/v1")

    return app


app = create_app()
