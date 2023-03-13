import logging
from pathlib import Path
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

    log_dir: Text = "log"
    log_access_filename: Text = "access.log"
    log_error_filename: Text = "error.log"
    log_service_filename: Text = "service.log"

    # Line Config
    line_channel_access_token: Text = ""
    line_channel_secret: Text = ""

    # Tracker Config
    tracker_store_service_url: Text = (
        "postgresql://postgres:default@tracker-store-service:5432/postgres"
    )
    tracker_store_message_encrypt_secret = "secret456"

    # Chat API Config
    chat_api_service_url: Text = "http://chat-api-service/api/chat/completion"


settings = Settings()


class LoggingConfig(BaseSettings):
    version = 1
    disable_existing_loggers = False
    formatters = {
        "basic_formatter": {
            "format": "%(asctime)s %(levelname)-8s %(name)s  - %(message)s",
        },
    }
    handlers = {
        "console_handler": {
            "level": settings.app_logger_level,
            "class": "rich.logging.RichHandler",
            "rich_tracebacks": True,
            "tracebacks_show_locals": False,
        },
        "file_handler": {
            "level": settings.app_logger_level,
            "class": "logging.handlers.RotatingFileHandler",
            "filename": (
                Path(settings.log_dir).joinpath(settings.log_service_filename).resolve()
            ),
            "formatter": "basic_formatter",
            "maxBytes": 2097152,
            "backupCount": 10,
        },
        "error_handler": {
            "level": "WARNING",
            "class": "logging.FileHandler",
            "filename": (
                Path(settings.log_dir).joinpath(settings.log_error_filename).resolve()
            ),
            "formatter": "basic_formatter",
        },
        "access_handler": {
            "level": settings.app_logger_level,
            "class": "logging.handlers.RotatingFileHandler",
            "filename": (
                Path(settings.log_dir).joinpath(settings.log_access_filename).resolve()
            ),
            "formatter": "basic_formatter",
            "maxBytes": 2097152,
            "backupCount": 10,
        },
    }
    loggers = {
        settings.app_logger_name: {
            "level": settings.app_logger_level,
            "handlers": ["console_handler", "file_handler", "error_handler"],
            "propagate": True,
        },
        settings.uvicorn_logger_name: {
            "level": settings.app_logger_level,
            "handlers": ["console_handler", "access_handler"],
            "propagate": True,
        },
    }


logging_config = LoggingConfig()
logging.config.dictConfig(logging_config)
logger = logging.getLogger(settings.app_logger_name)
uvicorn_logger = logging.getLogger(settings.uvicorn_logger_name)
