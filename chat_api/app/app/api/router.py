from fastapi import APIRouter

from app.api.v1.endpoints.chat.endpoint import router as chat_router
from app.api.v1.endpoints.gpt.endpoint import router as gpt_router


router = APIRouter()

router.include_router(chat_router, prefix="/chat", tags=["chat"])
router.include_router(gpt_router, prefix="/gpt", tags=["gpt"])
