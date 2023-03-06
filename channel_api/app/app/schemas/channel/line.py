from typing import Any, Dict, List, Text
from pydantic import BaseModel


class LineEvent(BaseModel):
    type: Text
    message: Dict[Text, Any]
    webhookEventId: Text
    deliveryContext: Dict[Text, Any]
    timestamp: int
    source: Dict
    replyToken: Text
    mode: Text


class LineCallback(BaseModel):
    destination: Text
    events: List[LineEvent]
