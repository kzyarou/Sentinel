from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.v1.api import api_router
from app.db.session import engine
from app.api.middleware import PayloadSizeMiddleware
from app.core.request_id import RequestIDMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan events."""
    # Startup
    # Database connection is handled lazily via get_db dependency
    yield
    # Shutdown
    await engine.dispose()


def create_application() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        debug=settings.DEBUG,
        lifespan=lifespan,
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # TODO: Configure properly for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Request ID middleware for correlation
    app.add_middleware(RequestIDMiddleware)
    
    # Payload size middleware for security
    app.add_middleware(
        PayloadSizeMiddleware,
        max_payload_size=settings.MAX_PAYLOAD_SIZE
    )

    # Include API router
    app.include_router(api_router, prefix=settings.API_V1_PREFIX)

    return app


app = create_application()
