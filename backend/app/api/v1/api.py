from fastapi import APIRouter

from app.api.v1.endpoints import health, events, detections

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(events.router, tags=["events"])
api_router.include_router(detections.router, tags=["detections"])
