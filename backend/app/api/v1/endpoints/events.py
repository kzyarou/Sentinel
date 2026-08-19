from fastapi import APIRouter, HTTPException, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any

from app.db.session import get_db
from app.schemas.event import EventCreate, Event as EventSchema
from app.services.validation import EventValidator, EventValidationError
from app.services.normalization import EventNormalizer
from app.services.event_service import EventService
from app.core.errors import (
    IngestionError,
    handle_ingestion_error
)
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/events", response_model=dict)
async def ingest_event(
    event_data: Dict[str, Any],
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Ingest a security event.
    
    This endpoint accepts security telemetry, validates it, normalizes it,
    and persists it to the database.
    
    Args:
        event_data: Raw event data from request body
        request: FastAPI request object
        db: Database session
        
    Returns:
        Dictionary with event ID and status
        
    Raises:
        HTTPException: If validation, normalization, or persistence fails
    """
    try:
        # Step 1: Validate payload size
        request_body = await request.body()
        EventValidator.validate_payload_size(request_body.decode('utf-8'))
        
        # Step 2: Sanitize input
        sanitized_data = EventValidator.sanitize_input(event_data)
        
        # Step 3: Validate required fields and field lengths
        EventValidator.validate_required_fields(sanitized_data)
        EventValidator.validate_field_lengths(sanitized_data)
        
        # Step 4: Validate schema
        validated_event = EventValidator.validate_event_data(sanitized_data)
        
        # Step 5: Normalize event
        normalized_event = EventNormalizer.normalize_event(sanitized_data)
        
        # Step 6: Persist event
        db_event = await EventService.create_event(db, normalized_event)
        
        # Step 7: Log successful ingestion
        logger.info(f"Event ingested successfully: {db_event.id}")
        
        return {
            "event_id": db_event.id,
            "status": "ingested"
        }
        
    except EventValidationError as e:
        logger.warning(f"Event validation failed: {e.message} (field: {e.field})")
        raise HTTPException(
            status_code=400,
            detail={
                "error": "validation_error",
                "message": e.message,
                "field": e.field
            }
        )
    except IngestionError as e:
        logger.error(f"Ingestion error: {e.message}")
        raise handle_ingestion_error(e)
    except Exception as e:
        logger.error(f"Unexpected error during event ingestion: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "internal_error",
                "message": "An unexpected error occurred during event ingestion"
            }
        )


@router.get("/events/{event_id}", response_model=EventSchema)
async def get_event(event_id: str, db: AsyncSession = Depends(get_db)):
    """
    Retrieve an event by ID.
    
    Args:
        event_id: Event ID to retrieve
        db: Database session
        
    Returns:
        Event object
        
    Raises:
        HTTPException: If event not found
    """
    try:
        db_event = await EventService.get_event_by_id(db, event_id)
        
        if not db_event:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "not_found",
                    "message": f"Event with ID {event_id} not found"
                }
            )
        
        return EventService.event_to_schema(db_event)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving event {event_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "internal_error",
                "message": "An error occurred while retrieving the event"
            }
        )