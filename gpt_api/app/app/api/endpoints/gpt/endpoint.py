from typing import Dict, List, Text, Union

import openai
import openai.error
from openai.openai_object import OpenAIObject
from pyassorted.datetime import Timer
from sanic import Blueprint
from sanic.exceptions import NotFound
from sanic.request import Request
from sanic.response import json as JSONResponse, text as PlainTextResponse
from sanic_ext import openapi, validate

from app.config import logger, openai_logger
from app.schemas.gpt import (
    ChatCompletionCall,
    ChatCompletionResponse,
    GPTChatMessage,
    Model,
    ModelsListResult,
)
from app.schemas.record import OpenAIRecord


blueprint = Blueprint(name="gpt")


@blueprint.get("", name="gpt.get")
@blueprint.get("/status", name="gpt.status.get")
async def status(request: "Request"):
    """Status check."""

    return PlainTextResponse("OK")


@blueprint.get("/models")
async def list_models(request: "Request"):
    """List models."""

    models_result: "OpenAIObject" = await openai.Model.alist()
    models_data: ModelsListResult = models_result.to_dict_recursive()
    models_list = models_data["data"]
    return JSONResponse(models_list)


@blueprint.get("/model/<model:str>")
async def model(request: "Request", model: Text):
    """Get model description."""

    try:
        models_result: "Model" = await openai.Model.aretrieve(model)
        models_data: Dict = models_result.to_dict_recursive()
    except openai.error.InvalidRequestError as e:
        raise NotFound(str(e))
    return JSONResponse(models_data)


@blueprint.post("/chat", name="gpt.chat.post")
@blueprint.post("/chat/completion", name="gpt.chat.completion.post")
@openapi.body(ChatCompletionCall, body_argument="chat_call")
@validate(json=ChatCompletionCall, body_argument="chat_call")
async def gpt_chat_completion(
    request: "Request",
    chat_call: Union[ChatCompletionCall, List[GPTChatMessage]],
    timer: "Timer",
):
    """Query chat completion."""

    if isinstance(chat_call, List):
        chat_call = ChatCompletionCall(messages=chat_call)
    logger.debug(f"Chat Completion Call: {chat_call.dict()}")

    completion_result: "OpenAIObject" = await openai.ChatCompletion.acreate(
        **chat_call.dict()
    )
    completion_res: ChatCompletionResponse = completion_result.to_dict_recursive()
    logger.debug(f"Chat Completion Response: {completion_res}")
    openai_logger.info(OpenAIRecord(**completion_res, time_cost=timer.click()))

    messages_res = [choice["message"] for choice in completion_res["choices"]]
    return JSONResponse(messages_res)
