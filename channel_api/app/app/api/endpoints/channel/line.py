from typing import Dict, Text

from fastapi import APIRouter, Body, Header, HTTPException, Request
from fastapi.responses import PlainTextResponse
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    MessageEvent,
    TextMessage,
    TextSendMessage,
)

from app.config import logger, settings

router = APIRouter()


line_bot_api = LineBotApi(settings.line_channel_access_token)
handler = WebhookHandler(settings.line_channel_secret)


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    line_bot_api.reply_message(
        event.reply_token, TextSendMessage(text=event.message.text)
    )


@router.post("/callback")
async def callback(request: Request, x_line_signature: Text = Header(...)):
    """Line callback endpoint."""

    line_callback = (await request.body()).decode("utf-8")
    logger.warning(line_callback)
    logger.warning(type(line_callback))
    logger.warning(x_line_signature)

    # handle webhook body
    try:
        handler.handle(line_callback, x_line_signature)
    except InvalidSignatureError:
        print(
            "Invalid signature. Please check your channel access token/channel secret."
        )
        raise HTTPException(status_code=400)

    return PlainTextResponse("OK")
