from typing import Dict, List, Text, TypedDict

import openai
from fastapi import APIRouter
from fastapi.params import Path
from fastapi.responses import JSONResponse
from openai.api_resources.model import Model
from openai.openai_object import OpenAIObject


router = APIRouter()


class ModelsListResult(TypedDict):
    object: Text
    data: List["Model"]


@router.get("/status")
async def status():
    """Status check."""

    return JSONResponse({"success": True})


@router.get("/models")
async def list_models():
    """List models."""

    models_result: "OpenAIObject" = openai.Model.list()
    models_data: ModelsListResult = models_result.to_dict_recursive()
    models_list = models_data["data"]
    return JSONResponse(models_list)


@router.get("/models/{model}")
async def model(model: Text = Path(..., example="ada")):
    """Get model description."""

    models_result: "Model" = openai.Model.retrieve(model)
    models_data: Dict = models_result.to_dict_recursive()
    return JSONResponse(models_data)
