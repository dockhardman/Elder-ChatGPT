import aiohttp
from fastapi import APIRouter, Body
from fastapi.responses import JSONResponse
from yarl import URL

from app.config import settings
from app.schemas.chat import ChatCall, ChatMessage, ChatResponse
from app.schemas.gpt import ChatCompletionCall, GPTChatMessage


router = APIRouter()


@router.post("/send", response_class=JSONResponse, response_model=ChatResponse)
@router.post("/", response_class=JSONResponse, response_model=ChatResponse)
@router.post("", response_class=JSONResponse, response_model=ChatResponse)
async def chat_send(chat_call: ChatCall = Body(...)):
    """Send chat message."""

    chat_res = ChatResponse(messages=[], metadata=chat_call.metadata)
    chat_completion_call = ChatCompletionCall(
        messages=[GPTChatMessage(role="user", content=chat_call.message)]
    )

    gpt_completion_url = URL(settings.host_gpt_service).with_path(
        settings.gpt_chat_completion_endpoint
    )
    async with aiohttp.ClientSession() as session:
        async with session.post(
            gpt_completion_url, json=chat_completion_call.dict()
        ) as resp:
            resp.raise_for_status()
            _data = await resp.json()
            for _message in _data:
                _gpt_message = GPTChatMessage(**_message)
                chat_res.messages.append(ChatMessage(text=_gpt_message.content))

    return chat_res
