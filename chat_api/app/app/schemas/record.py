from typing import Text

from pydantic import BaseModel


class EndpointRecord(BaseModel):
    """API Performance Schema"""

    name: Text
    version: Text
    method: Text
    path: Text
    status_code: int
    time_start: float
    time_end: float
    response_time: float
    response_type: Text

    class Config:
        schema_extra = {
            "example": {
                "name": "channel-api",
                "version": "0.0.1",
                "method": "GET",
                "path": "/api/chat/completion",
                "status_code": 200,
                "time_start": 1678789766.1022038,
                "time_end": 1678790378.131582,
                "response_time": 0.0001,
                "response_type": "application/json",
            }
        }
