from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import logging

logger = logging.getLogger(__name__)


class PayloadSizeMiddleware(BaseHTTPMiddleware):
    """
    Middleware to validate request payload size before processing.
    
    This prevents oversized payloads from reaching the application,
    which is important for security and resource management.
    """
    
    def __init__(self, app, max_payload_size: int = 1024 * 1024):  # 1MB default
        super().__init__(app)
        self.max_payload_size = max_payload_size
    
    async def dispatch(self, request: Request, call_next):
        """
        Process request and validate payload size.
        
        Args:
            request: Incoming request
            call_next: Next middleware/endpoint in chain
            
        Returns:
            Response from next middleware/endpoint
        """
        # Only validate content-type requests
        if request.method in ["POST", "PUT", "PATCH"]:
            content_length = request.headers.get("content-length")
            
            if content_length:
                try:
                    payload_size = int(content_length)
                    if payload_size > self.max_payload_size:
                        logger.warning(
                            f"Request rejected: payload size {payload_size} bytes "
                            f"exceeds maximum {self.max_payload_size} bytes"
                        )
                        return JSONResponse(
                            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                            content={
                                "error": "payload_too_large",
                                "message": f"Request payload ({payload_size} bytes) exceeds maximum allowed size ({self.max_payload_size} bytes)",
                                "max_size": self.max_payload_size
                            }
                        )
                except ValueError:
                    # Invalid content-length header, continue processing
                    pass
        
        response = await call_next(request)
        return response
