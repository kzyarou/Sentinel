from datetime import datetime
from typing import Dict, Any, Optional
from pydantic import ValidationError as PydanticValidationError

from app.schemas.event import EventCreate
from app.core.utils import sanitize_string


class EventValidationError(Exception):
    """Custom exception for event validation errors."""
    def __init__(self, message: str, field: Optional[str] = None):
        self.message = message
        self.field = field
        super().__init__(message)


class EventValidator:
    """Validates incoming security events."""
    
    # Maximum payload size in bytes (1MB default)
    MAX_PAYLOAD_SIZE = 1024 * 1024
    
    # Maximum field lengths
    MAX_EVENT_TYPE_LENGTH = 100
    MAX_SOURCE_LENGTH = 100
    MAX_HOST_LENGTH = 255
    MAX_USER_LENGTH = 255
    
    @staticmethod
    def validate_event_data(event_data: Dict[str, Any]) -> EventCreate:
        """
        Validate event data against the Event schema.
        
        Args:
            event_data: Raw event data from request
            
        Returns:
            Validated EventCreate object
            
        Raises:
            EventValidationError: If validation fails
        """
        try:
            # Use Pydantic for schema validation
            event = EventCreate(**event_data)
            return event
        except PydanticValidationError as e:
            # Extract the first error field for better error messages
            error_field = e.errors()[0].get('loc', ['unknown'])[-1] if e.errors() else 'unknown'
            error_message = e.errors()[0].get('msg', 'Validation failed') if e.errors() else 'Validation failed'
            raise EventValidationError(
                f"Invalid event data: {error_message}",
                field=error_field
            )
    
    @staticmethod
    def validate_payload_size(payload: str) -> None:
        """
        Validate that payload size is within limits.
        
        Args:
            payload: Raw request payload
            
        Raises:
            EventValidationError: If payload is too large
        """
        payload_size = len(payload.encode('utf-8'))
        if payload_size > EventValidator.MAX_PAYLOAD_SIZE:
            raise EventValidationError(
                f"Payload size ({payload_size} bytes) exceeds maximum allowed size ({EventValidator.MAX_PAYLOAD_SIZE} bytes)"
            )
    
    @staticmethod
    def validate_timestamp(timestamp: Any) -> datetime:
        """
        Validate and convert timestamp to datetime.
        
        Args:
            timestamp: Timestamp value from event
            
        Returns:
            Validated datetime object
            
        Raises:
            EventValidationError: If timestamp is invalid
        """
        if isinstance(timestamp, datetime):
            return timestamp
        
        if isinstance(timestamp, str):
            try:
                # Try ISO format parsing
                return datetime.fromisoformat(timestamp)
            except ValueError:
                raise EventValidationError("Invalid timestamp format. Use ISO format (e.g., 2024-01-01T00:00:00)")
        
        if isinstance(timestamp, (int, float)):
            try:
                # Try Unix timestamp
                return datetime.fromtimestamp(timestamp)
            except (ValueError, OSError):
                raise EventValidationError("Invalid Unix timestamp")
        
        raise EventValidationError("Invalid timestamp type. Must be datetime, ISO string, or Unix timestamp")
    
    @staticmethod
    def validate_field_lengths(event_data: Dict[str, Any]) -> None:
        """
        Validate that string fields are within length limits.
        
        Args:
            event_data: Event data to validate
            
        Raises:
            EventValidationError: If any field exceeds length limit
        """
        if 'event_type' in event_data and event_data['event_type']:
            event_type = str(event_data['event_type'])
            if len(event_type) > EventValidator.MAX_EVENT_TYPE_LENGTH:
                raise EventValidationError(
                    f"event_type exceeds maximum length of {EventValidator.MAX_EVENT_TYPE_LENGTH}"
                )
        
        if 'source' in event_data and event_data['source']:
            source = str(event_data['source'])
            if len(source) > EventValidator.MAX_SOURCE_LENGTH:
                raise EventValidationError(
                    f"source exceeds maximum length of {EventValidator.MAX_SOURCE_LENGTH}"
                )
        
        if 'host' in event_data and event_data['host']:
            host = str(event_data['host'])
            if len(host) > EventValidator.MAX_HOST_LENGTH:
                raise EventValidationError(
                    f"host exceeds maximum length of {EventValidator.MAX_HOST_LENGTH}"
                )
        
        if 'user' in event_data and event_data['user']:
            user = str(event_data['user'])
            if len(user) > EventValidator.MAX_USER_LENGTH:
                raise EventValidationError(
                    f"user exceeds maximum length of {EventValidator.MAX_USER_LENGTH}"
                )
    
    @staticmethod
    def validate_required_fields(event_data: Dict[str, Any]) -> None:
        """
        Validate that all required fields are present.
        
        Args:
            event_data: Event data to validate
            
        Raises:
            EventValidationError: If required fields are missing
        """
        required_fields = ['event_type', 'source', 'timestamp']
        missing_fields = [field for field in required_fields if field not in event_data or event_data[field] is None]
        
        if missing_fields:
            raise EventValidationError(f"Missing required fields: {', '.join(missing_fields)}")
    
    @staticmethod
    def sanitize_input(event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitize input data to prevent injection attacks.
        
        Args:
            event_data: Event data to sanitize
            
        Returns:
            Sanitized event data
        """
        sanitized = event_data.copy()
        
        # Sanitize string fields
        string_fields = ['event_type', 'source', 'host', 'user']
        for field in string_fields:
            if field in sanitized and sanitized[field] is not None:
                sanitized[field] = sanitize_string(str(sanitized[field]))
        
        return sanitized
