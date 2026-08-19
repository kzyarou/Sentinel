from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.event import Event
from app.schemas.event import EventCreate, Event as EventSchema
from app.core.utils import generate_event_id, validate_event_id


class EventService:
    """Service for event persistence and retrieval."""
    
    @staticmethod
    async def create_event(
        db: AsyncSession,
        event_data: EventCreate,
        event_id: Optional[str] = None
    ) -> Event:
        """
        Create and persist a new event.
        
        Args:
            db: Database session
            event_data: Validated event data
            event_id: Optional event ID (generates UUID if not provided)
            
        Returns:
            Created Event object
        """
        # Generate event ID if not provided
        if not event_id:
            event_id = generate_event_id()
        else:
            # Validate provided event ID
            if not validate_event_id(event_id):
                raise ValueError(f"Invalid event ID: {event_id}")
        
        # Create Event object
        db_event = Event(
            id=event_id,
            event_type=event_data.event_type,
            source=event_data.source,
            timestamp=event_data.timestamp,
            host=event_data.host,
            user=event_data.user,
            normalized_data=event_data.normalized_data,
            raw_data=event_data.raw_data
        )
        
        # Persist to database
        db.add(db_event)
        await db.commit()
        await db.refresh(db_event)
        
        return db_event
    
    @staticmethod
    async def get_event_by_id(db: AsyncSession, event_id: str) -> Optional[Event]:
        """
        Retrieve an event by ID.
        
        Args:
            db: Database session
            event_id: Event ID to retrieve
            
        Returns:
            Event object if found, None otherwise
        """
        result = await db.execute(
            select(Event).where(Event.id == event_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_events_by_source(
        db: AsyncSession,
        source: str,
        limit: int = 100
    ) -> list[Event]:
        """
        Retrieve events by source.
        
        Args:
            db: Database session
            source: Event source to filter by
            limit: Maximum number of events to return
            
        Returns:
            List of Event objects
        """
        result = await db.execute(
            select(Event)
            .where(Event.source == source)
            .order_by(Event.timestamp.desc())
            .limit(limit)
        )
        return result.scalars().all()
    
    @staticmethod
    async def get_events_by_type(
        db: AsyncSession,
        event_type: str,
        limit: int = 100
    ) -> list[Event]:
        """
        Retrieve events by type.
        
        Args:
            db: Database session
            event_type: Event type to filter by
            limit: Maximum number of events to return
            
        Returns:
            List of Event objects
        """
        result = await db.execute(
            select(Event)
            .where(Event.event_type == event_type)
            .order_by(Event.timestamp.desc())
            .limit(limit)
        )
        return result.scalars().all()
    
    @staticmethod
    async def get_events_by_host(
        db: AsyncSession,
        host: str,
        limit: int = 100
    ) -> list[Event]:
        """
        Retrieve events by host.
        
        Args:
            db: Database session
            host: Host to filter by
            limit: Maximum number of events to return
            
        Returns:
            List of Event objects
        """
        result = await db.execute(
            select(Event)
            .where(Event.host == host)
            .order_by(Event.timestamp.desc())
            .limit(limit)
        )
        return result.scalars().all()
    
    @staticmethod
    def event_to_schema(event: Event) -> EventSchema:
        """
        Convert Event model to Event schema.
        
        Args:
            event: Event model object
            
        Returns:
            Event schema object
        """
        return EventSchema(
            id=event.id,
            event_type=event.event_type,
            source=event.source,
            timestamp=event.timestamp,
            host=event.host,
            user=event.user,
            normalized_data=event.normalized_data,
            raw_data=event.raw_data,
            ingestion_timestamp=event.ingestion_timestamp
        )
