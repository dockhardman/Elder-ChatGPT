import json
from typing import List, Text

import aiohttp
from fastapi import APIRouter, Header, HTTPException, Request
from fastapi.responses import PlainTextResponse
from linebot import AsyncLineBotApi
from linebot.aiohttp_async_http_client import AiohttpAsyncHttpClient
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
from app.schemas.channel import LineCallback
from app.schemas.chat import Message
from app.schemas.tracker import Message as TrackerMessage
from app.utils.datetime import datetime_now


router = APIRouter()


line_bot_api = AsyncLineBotApi(
    settings.line_channel_access_token,
    async_http_client=AiohttpAsyncHttpClient(aiohttp.ClientSession()),
)
handler = AsyncWebhookHandler(settings.line_channel_secret)


async def get_user_records(
    source_user_id: Text, source_group_id: Text, record_length: int = 10
) -> List["TrackerMessage"]:
    records = (
        await TrackerMessage.objects.limit(record_length)
        .filter(source_user_id=source_user_id)
        .order_by(TrackerMessage.message_datetime.desc())
        .all()
    )
    return records


@handler.add(MessageEvent, message=TextMessage)
async def handle_message(event: MessageEvent):
    logger.debug(f"Line event {type(event)}: {event}")

    line_message: "TextMessage" = event.message
    line_source: "SourceUser" = event.source

    # Record user message
    user_message = TrackerMessage.from_line_text_message(
        text_message=line_message, source=line_source
    )
    await user_message.save()

    # Collect user message records
    records = await get_user_records(source_user_id=line_source.user_id)

    # Call Chat API
    chat_call_messages: List[Message] = []
    for record in records[::-1]:
        if record.source_type == "user" and record.message_type == "text":
            chat_call_messages.append(Message(role="user", content=record.message_text))
        elif record.source_type == "bot" and record.message_type == "text":
            chat_call_messages.append(
                Message(role="assistant", content=record.message_text)
            )
    chat_call_messages.append(Message(role="user", content=line_message.text))
    logger.debug(f"Call chat messages: {chat_call_messages}")

    res = requests.post(
        "http://chat-api-service/api/chat/completion",
        json=chat_call_messages,
    )
    messages = res.json()
    bot_text = messages[-1]["content"].strip()
    logger.debug(f"Return chat messages: {messages}")

    # Reply Line message
    await line_bot_api.reply_message(event.reply_token, TextSendMessage(text=bot_text))

    # Save bot message records
    bot_message = TrackerMessage(
        message_type="text",
        message_text=bot_text,
        source_type="bot",
        source_user_id=line_source.user_id,
        message_datetime=datetime_now(tz=settings.app_timezone),
    )
    await bot_message.save()


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
