from fastapi import APIRouter
from fastapi.responses import JSONResponse


router = APIRouter()


@router.get("/status")
async def status():
    """Status check."""

    return JSONResponse({"success": True})
