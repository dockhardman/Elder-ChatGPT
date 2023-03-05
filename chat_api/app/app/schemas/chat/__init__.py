from typing import List, Text, TypedDict

from openai.api_resources.model import Model
from pydantic import BaseModel


class ModelsListResult(TypedDict):
    object: Text
    data: List["Model"]


class ChatMessage(BaseModel):
    role: Text
    content: Text


class ChatMessageUser(ChatMessage):
    role: Text = "user"


class ChatMessageAssistant(ChatMessage):
    role: Text = "assistant"


class ChatCompletionCall(BaseModel):
    model: Text = "gpt-3.5-turbo"
    messages: List[ChatMessage]


class ChatUsage(TypedDict):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class ChatChoice(TypedDict):
    message: ChatMessage
    finish_reason: Text
    index: int


class ChatCompletionResponse(TypedDict):
    id: Text
    object: Text
    created: int
    model: Text
    usage: ChatUsage
    choices: List[ChatChoice]
