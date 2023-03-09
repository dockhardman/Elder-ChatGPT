import logging
from typing import Text

from pydantic import BaseSettings


class Settings(BaseSettings):
    # General
    app_name: str = "Channel-API"
    app_timezone: str = "Asia/Taipei"

    # Logging Config
    app_logger_name: str = "channel_api"
    app_logger_level: str = "DEBUG"
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


class LoggingConfig(BaseSettings):
    disable_existing_loggers = False
    formatters = {
        "base_formatter": {
            "format": "%(asctime)s %(levelname)-8s %(name)s  - %(message)s",
        },
        "message_formatter": {"format": "%(message)s"},
    }
    handlers = {
        "console_handler": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "base_formatter",
        }
    }
    loggers = {
        settings.app_logger_name: {
            "level": settings.app_logger_level,
            "handlers": ["console_handler"],
            "propagate": True,
        },
    }


logger = logging.getLogger(settings.app_logger_name)
uvicorn_logger = logging.getLogger(settings.uvicorn_logger_name)
