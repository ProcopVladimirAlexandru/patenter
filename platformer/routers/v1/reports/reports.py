from fastapi import APIRouter
from fastapi.responses import JSONResponse


router = APIRouter(prefix="/api/v1", tags=["reports"])


@router.post("/reports")
async def post_report() -> JSONResponse:
    return JSONResponse({"salut": "Da"})
