from fastapi import APIRouter

from app.config import logger


router = APIRouter()

# Channel Line
try:
    from app.api.endpoints.channel.line import router as line_router

    router.include_router(line_router, prefix="/line", tags=["line"])
    logger.info("Line router is loaded.")

except ImportError:
    logger.info("Line router is not loaded.")
