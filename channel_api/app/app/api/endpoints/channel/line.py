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

from app.config import settings


router = APIRouter()


line_bot_api = LineBotApi(settings.line_channel_access_token)
handler = WebhookHandler(settings.line_channel_secret)


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event: MessageEvent):
    res = requests.post(
        "http://chat-api-service/api/chat/completion",
        json=[{"role": "user", "content": "event.message.text"}],
    )
    messages = res.json()
    line_bot_api.reply_message(
        event.reply_token, TextSendMessage(text=messages[-1]["content"].strip())
    )


@router.post("/callback")
async def callback(request: Request, x_line_signature: Text = Header(...)):
    """Line callback endpoint."""

    # get request body as text
    line_callback_data = await request.body()
    line_callback_str = line_callback_data.decode("utf-8")

    # handle webhook body
    try:
        handler.handle(line_callback_str, x_line_signature)
    except InvalidSignatureError:
        print(
            "Invalid signature. Please check your channel access token/channel secret."
        )
        raise HTTPException(status_code=400)

    return PlainTextResponse("OK")
