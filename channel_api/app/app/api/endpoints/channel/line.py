import asyncio
import json
from typing import Text

from fastapi import APIRouter, Header, HTTPException, Request
from fastapi.responses import PlainTextResponse
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    MessageEvent,
    TextMessage,
    TextSendMessage,
)
import requests

from app.config import logger, settings
from app.schemas.channel.line import LineCallback
from app.schemas.tracker import Message as TrackerMessage
from app.utils.datetime import datetime_now


router = APIRouter()


line_bot_api = LineBotApi(settings.line_channel_access_token)
handler = WebhookHandler(settings.line_channel_secret)


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event: MessageEvent):
    res = requests.post(
        "http://chat-api-service/api/chat/completion",
        json=[{"role": "user", "content": event.message.text}],
    )
    messages = res.json()
    line_bot_api.reply_message(
        event.reply_token, TextSendMessage(text=messages[-1]["content"].strip())
    )

    user_message = TrackerMessage(
        message_type=event.message.type,
        message_text=event.message.text,
        source_type=event.source.type,
        source_user_id=event.source.get("userId", None),
        message_datetime=datetime_now(tz=settings.app_timezone),
    )
    loop = asyncio.get_running_loop()
    loop.run_until_complete(user_message.save())


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
        handler.handle(line_callback_str, x_line_signature)
    except InvalidSignatureError as e:
        logger.exception(e)
        logger.error(
            "Invalid signature. Please check your channel access token/channel secret."
        )
        raise HTTPException(status_code=400)

    return PlainTextResponse("OK")
