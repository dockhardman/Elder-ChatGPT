import json
from typing import List, Text
from pathlib import Path

import aiohttp
from fastapi import APIRouter, Body
from fastapi.responses import JSONResponse
from yarl import URL

from app.config import logger, settings
from app.schemas.chat import ChatCall, ChatMessage, ChatResponse
from app.schemas.gpt import ChatCompletionCall, GPTChatMessage


router = APIRouter()


async def read_sender_messages(
    sender: Text,
    record_length: int = 10,
) -> List["ChatMessage"]:
    message_filepath = Path(settings.messages_dir).joinpath(f"{sender}.json")
    if not message_filepath.parent.exists():
        message_filepath.parent.mkdir(parents=True, exist_ok=True)
    if not message_filepath.exists():
        return []

    with open(message_filepath, "r") as f:
        records = json.load(f)

    messages = [ChatMessage(**rec) for rec in records[-record_length:]]
    return messages


async def write_sender_messages(
    sender: Text,
    messages: List["ChatMessage"],
):
    message_filepath = Path(settings.messages_dir).joinpath(f"{sender}.json")
    if not message_filepath.parent.exists():
        message_filepath.parent.mkdir(parents=True, exist_ok=True)

    with open(message_filepath, "w") as f:
        json.dump([m.dict() for m in messages], f, ensure_ascii=False, indent=4)


@router.post("/send", response_class=JSONResponse, response_model=ChatResponse)
@router.post("/", response_class=JSONResponse, response_model=ChatResponse)
@router.post("", response_class=JSONResponse, response_model=ChatResponse)
async def chat_send(chat_call: ChatCall = Body(...)):
    """Send chat message."""

    chat_res = ChatResponse(messages=[], metadata=chat_call.metadata)

    user_message = ChatMessage(
        sender=chat_call.sender, type="user", text=chat_call.message
    )
    extra_messages = await read_sender_messages(sender=chat_call.sender)
    chat_completion_call = ChatCompletionCall(
        messages=[
            GPTChatMessage(role=m.type, content=m.text)
            for m in extra_messages
            if m.text and m.type in {"user", "assistant"}
        ]
        + [GPTChatMessage(role="user", content=chat_call.message)]
    )
    logger.debug(
        f"Request Chat Completion: {chat_completion_call.json(ensure_ascii=False, indent=4)}"
    )

    async with aiohttp.ClientSession() as session:
        async with session.post(
            URL(settings.host_gpt_service).with_path(
                settings.gpt_chat_completion_endpoint
            ),
            json=chat_completion_call.dict(),
        ) as resp:
            resp.raise_for_status()
            _data = await resp.json()
            for _message in _data:
                _gpt_message = GPTChatMessage(**_message)
                res_message = ChatMessage(
                    sender=chat_call.sender,
                    type="assistant",
                    text=_gpt_message.content,
                )
                chat_res.messages.append(res_message)
                logger.debug(
                    "Response Chat Completion: "
                    + f"{_gpt_message.json(ensure_ascii=False, indent=4)}"
                )

    await write_sender_messages(
        sender=chat_call.sender, messages=extra_messages + [user_message, res_message]
    )
    return chat_res
