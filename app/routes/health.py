from fastapi import APIRouter
from logger import logger
from schemas import HealthResponse

router = APIRouter(prefix="/api/health", tags=["Health"])


@router.get("/check", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Check if the service is healthy"""
    logger.info("Health check requested")
    return HealthResponse(message="Service is healthy")
