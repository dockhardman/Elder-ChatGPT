import logging
import json
from pathlib import Path
from typing import Any, Dict, Text

from pydantic import BaseModel, BaseSettings


def is_serializable(obj: Any):
    try:
        if isinstance(obj, BaseModel):
            obj.json()
        else:
            json.dumps(obj)
        return True
    except TypeError:
        return False


class Settings(BaseSettings):
    # General
    app_name: str = "Channel-API"
    app_version: str = "0.3.1"
    app_timezone: str = "Asia/Taipei"

    # Logging Config
    app_logger_name: str = "channel_api"
    app_logger_level: str = "DEBUG"
    uvicorn_logger_name: str = "uvicorn.error"
    endpoint_logger_name: str = "endpoint"

    log_dir: Text = "log"
    log_access_filename: Text = "access.log"
    log_error_filename: Text = "error.log"
    log_service_filename: Text = "service.log"
    log_endpoint_performance_filename: Text = "endpoint.log"

    # Line Config
    line_channel_access_token: Text = ""
    line_channel_secret: Text = ""

    # Tracker Config
    tracker_store_service_url: Text = (
        "postgresql://postgres:default@fami-tracker-store-service:5432/postgres"
    )
    tracker_store_message_encrypt_secret = "secret456"

    # Chat API Config
    host_chat_service = "http://fami-chat-api-service"
    chat_send_endpoint = "/api/chat"


settings = Settings()


class LoggingConfig(BaseSettings):
    version = 1
    disable_existing_loggers = False
    formatters = {
        "basic_formatter": {
            "format": "%(asctime)s %(levelname)-8s %(name)s  - %(message)s",
        },
        "json_formatter": {
            "format": "%(json_message)s",
        },
    }
    handlers = {
        "console_handler": {
            "level": settings.app_logger_level,
            "class": "rich.logging.RichHandler",
            "rich_tracebacks": True,
            "show_path": False,
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
        "endpoint_performance_handler": {
            "level": settings.app_logger_level,
            "class": "logging.FileHandler",
            "filename": (
                Path(settings.log_dir)
                .joinpath(settings.log_endpoint_performance_filename)
                .resolve()
            ),
            "formatter": "json_formatter",
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
        settings.endpoint_logger_name: {
            "level": settings.app_logger_level,
            "handlers": ["endpoint_performance_handler"],
            "propagate": True,
        },
    }


default_log_record_factory = logging.getLogRecordFactory()


def custom_log_record_factory(*args, **kwargs):
    record = default_log_record_factory(*args, **kwargs)

    if is_serializable(record.msg):
        if isinstance(record.msg, BaseModel):
            record.json_message = record.msg.json(ensure_ascii=False)
        elif isinstance(record.msg, Dict):
            record.json_message = json.dumps(record.msg, ensure_ascii=False)
    return record


logging_config = LoggingConfig()
logging.config.dictConfig(logging_config)

default_factory = logging.getLogRecordFactory()
logging.setLogRecordFactory(custom_log_record_factory)

logger = logging.getLogger(settings.app_logger_name)
uvicorn_logger = logging.getLogger(settings.uvicorn_logger_name)
endpoint_logger = logging.getLogger(settings.endpoint_logger_name)
