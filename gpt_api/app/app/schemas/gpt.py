from typing import List, Text, TypedDict

from openai.api_resources.model import Model
from pydantic import BaseModel


class ModelsListResult(TypedDict):
    object: Text
    data: List["Model"]


class GPTChatMessage(BaseModel, anystr_strip_whitespace=True):
    role: Text  # user, assistant
    content: Text


class ChatCompletionCall(BaseModel, anystr_strip_whitespace=True):
    model: Text = "gpt-3.5-turbo"
    messages: List[GPTChatMessage]


class ChatUsage(TypedDict):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class ChatChoice(TypedDict):
    message: GPTChatMessage
    finish_reason: Text
    index: int


class ChatCompletionResponse(TypedDict):
    id: Text
    object: Text
    created: int
    model: Text
    usage: ChatUsage
    choices: List[ChatChoice]
