from typing import Optional, List, TYPE_CHECKING
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.event import Event
from app.detection import DetectionEngine
from app.detection.rule_seeds import RuleSeeds
import logging

if TYPE_CHECKING:
    from app.models.detection import Detection as DetectionModel

logger = logging.getLogger(__name__)


class EventProcessingService:
    """Service for coordinating event processing with detection."""
    
    @staticmethod
    async def process_event_with_detection(
        db: AsyncSession,
        event: Event
    ) -> List['DetectionModel']:
        """
        Process an event through the detection engine.
        
        Args:
            db: Database session
            event: The event to process
            
        Returns:
            List of Detection objects created from matching rules
        """
        try:
            # Initialize detection engine
            detection_engine = DetectionEngine(db)
            
            # Evaluate event against rules
            detections = await detection_engine.evaluate_event(event)
            
            logger.info(
                f"Detection evaluation complete for event {event.id}: "
                f"{len(detections)} detections created"
            )
            
            return detections
            
        except Exception as e:
            logger.error(
                f"Detection evaluation failed for event {event.id}: {str(e)}"
            )
            # Return empty list - event is still processed even if detection fails
            return []
    
    @staticmethod
    async def ensure_rules_seeded(db: AsyncSession) -> None:
        """
        Ensure initial detection rules are seeded in the database.
        
        This is called during event processing to ensure rules exist.
        
        Args:
            db: Database session
        """
        try:
            await RuleSeeds.seed_initial_rules(db)
            logger.info("Detection rules seeding check complete")
        except Exception as e:
            logger.error(f"Failed to seed detection rules: {str(e)}")
            # Continue even if seeding fails