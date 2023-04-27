import openai
import sanic
from sanic.request import Request
from sanic.response import text as PlainTextResponse

from app.config import logger, settings


def create_app():
    app = sanic.Sanic(
        name=settings.app_name,
    )

    @app.before_server_start
    async def before_server_start(*_):
        openai.organization = settings.openai_organization
        openai.api_key = settings.openai_api_key
        logger.debug(f"Set OpenAI credentials for {openai.organization}")

    @app.get("/")
    async def root(request: "Request"):
        return PlainTextResponse("OK")

    # Router
    from app.api.blueprint import blueprint

    app.blueprint(blueprint)

    return app


app = create_app()
