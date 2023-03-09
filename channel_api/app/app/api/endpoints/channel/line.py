import json
from typing import Text

from fastapi import APIRouter, Header, HTTPException, Request
from fastapi.responses import PlainTextResponse
from linebot import AsyncLineBotApi
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    MessageEvent,
    SourceUser,
    TextMessage,
    TextSendMessage,
)
import requests

from app.bot.line.handler import AsyncWebhookHandler
from app.config import logger, settings
from app.schemas.channel.line import LineCallback
from app.schemas.tracker import Message as TrackerMessage
from app.utils.datetime import datetime_now


router = APIRouter()


line_bot_api = AsyncLineBotApi(settings.line_channel_access_token)
handler = AsyncWebhookHandler(settings.line_channel_secret)


@handler.add(MessageEvent, message=TextMessage)
async def handle_message(event: MessageEvent):
    logger.debug(f"Line event {type(event)}: {event}")

    line_message: "TextMessage" = event.message
    line_source: "SourceUser" = event.source

    chat_call_messages = [{"role": "user", "content": line_message.text}]
    logger.debug(f"Call chat messages: {chat_call_messages}")

    res = requests.post(
        "http://chat-api-service/api/chat/completion",
        json=chat_call_messages,
    )
    messages = res.json()
    logger.debug(f"Return chat messages: {messages}")

    await line_bot_api.reply_message(
        event.reply_token, TextSendMessage(text=messages[-1]["content"].strip())
    )

    user_message = TrackerMessage(
        message_type=line_message.type,
        message_text=line_message.text,
        source_type=line_source.type,
        source_user_id=line_source.user_id,
        message_datetime=datetime_now(tz=settings.app_timezone),
    )
    # uvicorn_logger.debug(user_message)
    # loop = asyncio.get_running_loop()
    # loop.run_until_complete(user_message.save())


@router.post("/callback")
async def callback(request: Request, x_line_signature: Text = Header(...)):
    """Line callback endpoint."""

    # get request body as text
    line_callback_data = await request.body()
    line_callback = LineCallback(**json.loads(line_callback_data))
    logger.debug(f"line_callback: {line_callback.json(ensure_ascii=False)}")

    line_callback_str = line_callback_data.decode("utf-8")

    # handle webhook body
    try:
        await handler.async_handle(line_callback_str, x_line_signature)
    except InvalidSignatureError as e:
        logger.exception(e)
        logger.error(
            "Invalid signature. Please check your channel access token/channel secret."
        )
        raise HTTPException(status_code=400)

    return PlainTextResponse("OK")
