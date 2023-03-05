import logging

from pydantic import BaseSettings


class Settings(BaseSettings):
    # General
    app_name: str = "Channel-API"
    logger_name: str = "channel_api"


settings = Settings()
logger = logging.getLogger(settings.logger_name)
