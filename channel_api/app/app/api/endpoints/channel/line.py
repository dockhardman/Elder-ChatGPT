import json
from typing import Text

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

from app.bot.line.handler import AsyncWebhookHandler
from app.config import logger, settings
from app.resources.chat import requests_chat_api
from app.schemas.channel import LineCallback
from app.schemas.chat import ChatCall


router = APIRouter()


line_bot_api = AsyncLineBotApi(
    settings.line_channel_access_token,
    async_http_client=AiohttpAsyncHttpClient(aiohttp.ClientSession()),
)
handler = AsyncWebhookHandler(settings.line_channel_secret)


@handler.add(MessageEvent, message=TextMessage)
async def handle_message(event: MessageEvent):
    """Handle Line text message.

    Parameters
    ----------
    event : MessageEvent
        Line message event.
    """

    logger.debug(f"Line event {type(event)}: {event}")

    line_message: "TextMessage" = event.message
    line_source: "SourceUser" = event.source

    # Call Chat API
    chat_call = ChatCall(
        sender=f"{line_source.user_id}@Line+User",
        message=line_message.text,
        metadata={"line_event": event.as_json_dict(), "channel": "Line+User"},
    )
    logger.debug(f"Request chat call: {chat_call}")

    chat_res = await requests_chat_api(chat_call=chat_call)
    logger.debug(f"Return chat response: {chat_res}")

    # Reply Line message
    for chat_message in chat_res.messages:
        if chat_message.text:
            await line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=chat_message.text.strip().replace("\n\n", "\n")),
            )
            break  # only reply first message


@router.post("/callback")
async def callback(request: Request, x_line_signature: Text = Header(...)):
    """Line callback endpoint.

    Parameters
    ----------
    request : Request
        FastAPI request.
    x_line_signature : Text, optional
        Line signature, must be set in header.
    """

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
