from sanic import Blueprint

from app.api.endpoints.gpt.endpoint import blueprint as gpt_blueprint


gpt_bp_group = Blueprint.group(gpt_blueprint, url_prefix="/gpt")
blueprint = Blueprint.group(gpt_bp_group, url_prefix="/api")
