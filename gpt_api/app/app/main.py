import openai
import sanic
from pyassorted.datetime import Timer
from sanic.request import Request
from sanic.response import text as PlainTextResponse

from app.config import logger, settings


def get_timer(request: "Request") -> "Timer":
    timer = Timer()
    timer.click()
    return timer


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

    app.ext.add_dependency(Timer, get_timer)

    # Blueprint
    from app.api.blueprint import blueprint as api_blueprint

    app.blueprint(api_blueprint)

    return app


app = create_app()
