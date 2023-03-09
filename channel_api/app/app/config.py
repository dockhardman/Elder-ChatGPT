import logging
from typing import Text

from pydantic import BaseSettings


class Settings(BaseSettings):
    # General
    app_name: str = "Channel-API"
    app_timezone: str = "Asia/Taipei"

    # Logging Config
    app_logger_name: str = "channel_api"
    uvicorn_logger_name: str = "uvicorn.error"

    # Line Config
    line_channel_access_token: Text = ""
    line_channel_secret: Text = ""

    # Tracker Config
    tracker_store_service_url: Text = (
        "postgresql+aiopg:///postgres:default@tracker-store-service:5452/postgres"
    )
    tracker_store_message_encrypt_secret = "secret456"


settings = Settings()
logger = logging.getLogger(settings.app_logger_name)
uvicorn_logger = logging.getLogger(settings.uvicorn_logger_name)
