from typing import List, Text

import aiohttp
from yarl import URL

from app.config import settings
from app.schemas.chat import Message


async def requests_chat_api(
    messages: List[Message], url: Text = settings.chat_api_service_url
) -> List[Message]:
    """Requests chat API.

    Parameters
    ----------
    messages : List[Message]
        Messages.
    url : Text, optional
        Chat API URL, by default settings.chat_api_service_url

    Returns
    -------
    Message
        Response message.
    """

    async with aiohttp.ClientSession() as session:
        async with session.post(URL(url), json=messages) as resp:
            resp.raise_for_status()
            return_messages: List[Message] = await resp.json()

    return return_messages
