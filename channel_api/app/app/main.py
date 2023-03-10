import logging
from typing import TYPE_CHECKING

import fastapi
from fastapi.responses import PlainTextResponse

from app.config import logger, settings, uvicorn_logger

if TYPE_CHECKING:
    import databases


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
