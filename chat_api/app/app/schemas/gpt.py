from typing import List, Text

from pydantic import BaseModel


class GPTChatMessage(BaseModel, anystr_strip_whitespace=True):
    role: Text
    content: Text


class GPTChatMessageUser(GPTChatMessage, anystr_strip_whitespace=True):
    role: Text = "user"


class GPTChatMessageAssistant(GPTChatMessage, anystr_strip_whitespace=True):
    role: Text = "assistant"


class ChatCompletionCall(BaseModel, anystr_strip_whitespace=True):
    model: Text = "gpt-3.5-turbo"
    messages: List[GPTChatMessage]
