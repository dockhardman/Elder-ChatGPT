import logging

import openai
import sanic
from sanic import response
from sanic import request

from app.config import settings

logger = logging.getLogger(settings.logger_name)


def create_app():
    app = sanic.Sanic(
        name=settings.app_name,
    )

    @app.main_process_start
    async def main_process_start(*_):
        openai.organization = settings.openai_organization
        openai.api_key = settings.openai_api_key

    @app.get("/")
    async def root(request: request.Request):
        return response.text("OK")

    # Router

    return app


app = create_app()
