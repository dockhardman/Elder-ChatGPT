import logging
import time
from typing import TYPE_CHECKING

import fastapi
from fastapi.responses import PlainTextResponse

from app.config import endpoint_logger, logger, settings, uvicorn_logger
from app.schemas.performance import EndpointPerformance

if TYPE_CHECKING:
    import databases
    from starlette.middleware.base import _StreamingResponse


logger = logging.getLogger(settings.app_logger_name)


def create_app():
    app = fastapi.FastAPI(
        title=settings.app_name,
    )

    # Databases
    from app.db.tracker_store import create_message_database, message_database

    app.state.message_database = message_database

    # ASGI Events
    @app.on_event("startup")
    async def startup() -> None:
        message_database_: "databases.Database" = app.state.message_database
        if not message_database_.is_connected:
            await message_database_.connect()
        logger.debug("Message database is connected.")
        create_message_database()
        logger.debug("Message metadata is created.")

    @app.on_event("shutdown")
    async def shutdown() -> None:
        message_database_: "databases.Database" = app.state.message_database
        if message_database_.is_connected:
            await message_database_.disconnect()
        logger.debug("Message database is disconnected.")

    @app.middleware("http")
    async def log_api_performance(request: "fastapi.Request", call_next):
        time_start = time.time()
        response: "_StreamingResponse" = await call_next(request)
        time_end = time.time()
        timecost = time_end - time_start

        endpoint_logger.info(
            EndpointPerformance(
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

    # Root Route
    @app.get("/")
    async def root():
        logger.debug("OK")
        uvicorn_logger.debug("OK")
        return PlainTextResponse("OK")

    # Routers
    from app.api.router import router

    app.include_router(router, prefix=f"/channel")

    return app


app = create_app()
