from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter()

@router.get("/test-endpoint")
async def test_endpoint():
    return JSONResponse(content={"message": "This is a test endpoint"})
