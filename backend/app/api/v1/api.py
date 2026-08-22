from fastapi import APIRouter

from app.api.v1.endpoints import health, ai_analysis

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(ai_analysis.router, tags=["ai-analysis"])
