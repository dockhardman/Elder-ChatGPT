from typing import Text

import aiohttp
from yarl import URL

from app.config import settings
from app.schemas.chat import ChatCall, ChatResponse


async def requests_chat_api(
    chat_call: "ChatCall",
    url: Text = URL(settings.host_gpt_service).with_path(
        settings.gpt_chat_completion_endpoint
    ),
) -> "ChatResponse":
    async with aiohttp.ClientSession() as session:
        async with session.post(URL(url), json=chat_call.dict()) as resp:
            resp.raise_for_status()
            _data = await resp.json()
            chat_res = ChatResponse(**_data)
    return chat_res
