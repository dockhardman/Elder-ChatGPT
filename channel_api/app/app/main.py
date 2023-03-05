import logging

import fastapi
from fastapi.responses import PlainTextResponse

from app.config import settings


logger = logging.getLogger(settings.logger_name)


def create_app():
    app = fastapi.FastAPI(
        title=settings.app_name,
    )

    @app.get("/")
    async def root():
        return PlainTextResponse("OK")

    # Router

    return app


app = create_app()
