import logging
import time
from typing import TYPE_CHECKING

import fastapi
import openai
from fastapi.responses import PlainTextResponse

from app.schemas.record import EndpointRecord
from app.config import endpoint_logger, settings

if TYPE_CHECKING:
    from starlette.middleware.base import _StreamingResponse


logger = logging.getLogger(settings.logger_name)


def create_app():
    app = fastapi.FastAPI(
        title=settings.app_name,
    )

    @app.on_event("startup")
    async def on_event_startup():
        openai.organization = settings.openai_organization
        openai.api_key = settings.openai_api_key

    @app.middleware("http")
    async def log_api_performance(request: "fastapi.Request", call_next):
        time_start = time.time()
        response: "_StreamingResponse" = await call_next(request)
        time_end = time.time()
        timecost = time_end - time_start

        endpoint_logger.info(
            EndpointRecord(
                name=settings.app_name,
                version=settings.app_version,
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                time_start=time_start,
                time_end=time_end,
                response_time=timecost,
                response_type=response.headers["Content-Type"],
            )
        )
        response.headers["X-Process-Time"] = str(timecost)
        return response

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
