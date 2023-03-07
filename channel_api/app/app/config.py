import logging
from typing import Text

from pydantic import BaseSettings


class Settings(BaseSettings):
    # General
    app_name: str = "Channel-API"
    logger_name: str = "channel_api"

    # Line Config
    line_channel_access_token: Text = ""
    line_channel_secret: Text = ""


settings = Settings()
logger = logging.getLogger(settings.logger_name)
