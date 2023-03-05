from typing import Dict, List, Text, Union

import openai
from fastapi import APIRouter, Body, Path
from fastapi.responses import JSONResponse
from openai.api_resources.model import Model
from openai.openai_object import OpenAIObject

from app.schemas.chat import (
    ChatCompletionCall,
    ChatCompletionResponse,
    ChatMessage,
    ModelsListResult,
)


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
    "/completion", response_class=JSONResponse, response_model=List[ChatMessage]
)
async def chat_completion(
    chat_call: Union[ChatCompletionCall, List[ChatMessage]] = Body(
        ..., example=[{"role": "user", "content": "hello"}]
    )
):
    """Query chat completion."""

    if isinstance(chat_call, List):
        chat_call = ChatCompletionCall(messages=chat_call)

    completion_result: "OpenAIObject" = await openai.ChatCompletion.acreate(
        **chat_call.dict()
    )
    completion_res: ChatCompletionResponse = completion_result.to_dict_recursive()
    messages_res = [choice["message"] for choice in completion_res["choices"]]

    return messages_res
