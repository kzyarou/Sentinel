from fastapi import APIRouter

from app.api.v1.endpoints import health, events, detections, findings, ai_analysis, auth, audit_logs

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(auth.router, tags=["auth"])
api_router.include_router(audit_logs.router, tags=["audit-logs"])
api_router.include_router(events.router, tags=["events"])
api_router.include_router(detections.router, tags=["detections"])
api_router.include_router(findings.router, tags=["findings"])
api_router.include_router(ai_analysis.router, tags=["ai-analysis"])
