import time
from typing import Any, Dict, List, Optional, Text

from pydantic import BaseModel, Field


class ChatMessage(BaseModel, anystr_strip_whitespace=True):
    text: Optional[Text] = None
    object: Optional[Dict] = None
    image: Optional[Any] = None
    audio: Optional[Any] = None
    url: Optional[Text] = None
    timestamp: Optional[float] = Field(default_factory=time.time)


class ChatCall(BaseModel, anystr_strip_whitespace=True):
    sender: Text
    message: Text
    metadata: Dict = Field(default_factory=dict)


class ChatResponse(BaseModel):
    messages: List[ChatMessage]
    metadata: Dict = Field(default_factory=dict)
