import time
from typing import Dict, List, Text, Union

import openai
from fastapi import APIRouter, Body, Depends, Path
from fastapi.responses import JSONResponse
from openai.api_resources.model import Model
from openai.openai_object import OpenAIObject

from app.config import openai_logger
from app.schemas.gpt import (
    ChatCompletionCall,
    ChatCompletionResponse,
    GPTChatMessage,
    ModelsListResult,
)
from app.schemas.record import OpenAIRecord
from app.utils.common import async_time

router = APIRouter()


@router.get("/status")
async def status():
    """Status check."""

    return JSONResponse({"success": True})


@router.get("/models")
async def list_models():
    """List models."""

    models_result: "OpenAIObject" = await openai.Model.alist()
    models_data: ModelsListResult = models_result.to_dict_recursive()
    models_list = models_data["data"]
    return JSONResponse(models_list)


@router.get("/models/{model}")
async def model(model: Text = Path(..., example="ada")):
    """Get model description."""

    models_result: "Model" = await openai.Model.aretrieve(model)
    models_data: Dict = models_result.to_dict_recursive()
    return JSONResponse(models_data)


@router.post(
    "/chat/completion", response_class=JSONResponse, response_model=List[GPTChatMessage]
)
async def gpt_chat_completion(
    chat_call: Union[ChatCompletionCall, List[GPTChatMessage]] = Body(
        ..., example=[{"role": "user", "content": "hello"}]
    ),
    time_start: float = Depends(async_time),
):
    """Query chat completion."""

    if isinstance(chat_call, List):
        chat_call = ChatCompletionCall(messages=chat_call)

    completion_result: "OpenAIObject" = await openai.ChatCompletion.acreate(
        **chat_call.dict()
    )
    completion_res: ChatCompletionResponse = completion_result.to_dict_recursive()
    messages_res = [choice["message"] for choice in completion_res["choices"]]

    time_end = time.time()
    openai_logger.info(
        OpenAIRecord(
            **completion_res,
            timeStart=time_start,
            timeEnd=time_end,
            timeCost=time_end - time_start
        )
    )
    return messages_res
