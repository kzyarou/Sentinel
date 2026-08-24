import uuid
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import logging

logger = logging.getLogger(__name__)


class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add unique request IDs to all requests for correlation.
    
    This middleware generates a unique ID for each request and adds it to the
    request state for use in logging, audit trails, and debugging.
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request with request ID generation.
        
        Args:
            request: Incoming HTTP request
            call_next: Next middleware or route handler
            
        Returns:
            HTTP response with request ID header
        """
        # Generate or extract request ID
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        
        # Add request ID to request state for use in handlers
        request.state.request_id = request_id
        
        # Process request
        response = await call_next(request)
        
        # Add request ID to response headers for client correlation
        response.headers["X-Request-ID"] = request_id
        
        logger.debug(f"Request ID: {request_id} for {request.method} {request.url.path}")
        
        return response


def get_request_id(request: Request) -> str:
    """
    Get the request ID from the request state.
    
    Args:
        request: FastAPI request object
        
    Returns:
        Request ID string
    """
    return getattr(request.state, "request_id", "unknown")