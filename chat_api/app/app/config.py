import logging

from pydantic import BaseSettings


class Settings(BaseSettings):
    # General
    app_name: str = "Chat-API"
    logger_name: str = "chat_api"

    # OpenAI Config
    openai_api_key: str = "sk-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
    openai_organization: str = "org-************************"


settings = Settings()
logger = logging.getLogger(settings.logger_name)
