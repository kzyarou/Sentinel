from typing import Optional, Any
from fastapi import HTTPException, status


class IngestionError(Exception):
    """Base exception for ingestion errors."""
    def __init__(self, message: str, details: Optional[dict] = None):
        self.message = message
        self.details = details or {}
        super().__init__(message)


class ValidationError(IngestionError):
    """Exception for validation errors."""
    def __init__(self, message: str, field: Optional[str] = None, details: Optional[dict] = None):
        self.field = field
        super().__init__(message, details)


class NormalizationError(IngestionError):
    """Exception for normalization errors."""
    pass


class PersistenceError(IngestionError):
    """Exception for persistence errors."""
    pass


class AuthenticationError(IngestionError):
    """Exception for authentication errors."""
    pass


class AuthorizationError(IngestionError):
    """Exception for authorization errors."""
    pass


def handle_ingestion_error(error: IngestionError) -> HTTPException:
    """
    Convert ingestion errors to HTTP responses.
    
    This prevents internal database errors from being exposed to clients.
    
    Args:
        error: IngestionError to handle
        
    Returns:
        HTTPException with appropriate status code and message
    """
    if isinstance(error, ValidationError):
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "validation_error",
                "message": error.message,
                "field": error.field,
                "details": error.details
            }
        )
    elif isinstance(error, NormalizationError):
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "normalization_error",
                "message": error.message,
                "details": error.details
            }
        )
    elif isinstance(error, PersistenceError):
        # Don't expose internal database errors
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "persistence_error",
                "message": "Failed to persist event"
            }
        )
    elif isinstance(error, AuthenticationError):
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": "authentication_error",
                "message": error.message
            }
        )
    elif isinstance(error, AuthorizationError):
        return HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": "authorization_error",
                "message": error.message
            }
        )
    else:
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "internal_error",
                "message": "An internal error occurred"
            }
        )
