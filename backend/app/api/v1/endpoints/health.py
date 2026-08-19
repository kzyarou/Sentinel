from fastapi import APIRouter, HTTPException

from app.db.session import check_db_connection

router = APIRouter()


@router.get("/health")
async def health_check():
    """Basic health check endpoint."""
    return {"status": "ok"}


@router.get("/health/ready")
async def readiness_check():
    """Readiness check endpoint with database connectivity."""
    db_connected = await check_db_connection()
    
    if db_connected:
        return {
            "status": "ready",
            "database": "connected"
        }
    else:
        raise HTTPException(
            status_code=503,
            detail="Service unavailable - database connection failed"
        )
