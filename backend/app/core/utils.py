import uuid
from typing import Optional


def generate_event_id() -> str:
    """Generate a unique event ID using UUID4."""
    return str(uuid.uuid4())


def generate_uuid() -> str:
    """Generate a unique UUID using UUID4."""
    return str(uuid.uuid4())


def validate_event_id(event_id: str) -> bool:
    """Validate that a string is a valid UUID."""
    try:
        uuid.UUID(event_id)
        return True
    except (ValueError, AttributeError):
        return False


def sanitize_string(value: str, max_length: Optional[int] = None) -> str:
    """Sanitize a string by removing potentially dangerous characters."""
    if not isinstance(value, str):
        return ""
    
    # Remove null bytes and other potentially dangerous characters
    sanitized = value.replace("\x00", "")
    
    # Trim whitespace
    sanitized = sanitized.strip()
    
    # Apply max length if specified
    if max_length and len(sanitized) > max_length:
        sanitized = sanitized[:max_length]
    
    return sanitized
