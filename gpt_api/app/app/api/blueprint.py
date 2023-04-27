from sanic import Blueprint

from app.api.endpoints.gpt.endpoint import blueprint as gpt_blueprint


blueprint = Blueprint.group(gpt_blueprint, url_prefix="/gpt")
