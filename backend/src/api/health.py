"""
Health Check Endpoint
Verifies all services are operational
"""

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from src.database import db, qdrant
import time

router = APIRouter()


@router.get("/health")
async def health_check():
    """
    Health check endpoint - verifies database and vector store connections

    Returns:
        200: All services healthy
        503: One or more services unavailable
    """
    health_status = {
        "status": "healthy",
        "timestamp": time.time(),
        "services": {},
    }

    # Check Postgres
    try:
        await db.fetchval("SELECT 1")
        health_status["services"]["postgres"] = "healthy"
    except Exception as e:
        health_status["services"]["postgres"] = f"unhealthy: {str(e)}"
        health_status["status"] = "degraded"

    # Check Qdrant
    try:
        info = await qdrant.get_collection_info()
        health_status["services"]["qdrant"] = {
            "status": "healthy",
            "points_count": info["points_count"],
        }
    except Exception as e:
        health_status["services"]["qdrant"] = f"unhealthy: {str(e)}"
        health_status["status"] = "degraded"

    status_code = (
        status.HTTP_200_OK
        if health_status["status"] == "healthy"
        else status.HTTP_503_SERVICE_UNAVAILABLE
    )

    return JSONResponse(status_code=status_code, content=health_status)
