from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.db.session import get_db
from app.schemas.detection_rule import DetectionRule as DetectionRuleSchema
from app.schemas.detection import Detection as DetectionSchema
from app.services.detection_service import DetectionService
from app.detection.rule_seeds import RuleSeeds
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/detections/seed-rules", response_model=dict)
async def seed_detection_rules(db: AsyncSession = Depends(get_db)):
    """
    Seed the database with initial detection rules.
    
    This endpoint creates the initial set of detection rules if they don't exist.
    It's idempotent - running it multiple times won't create duplicates.
    
    Args:
        db: Database session
        
    Returns:
        Dictionary with seeding status and rule count
    """
    try:
        created_rules = await RuleSeeds.seed_initial_rules(db)
        
        return {
            "status": "success",
            "message": f"Seeded {len(created_rules)} detection rules",
            "rules_count": len(created_rules),
            "rules": [
                {
                    "name": rule.name,
                    "version": rule.version,
                    "enabled": rule.enabled
                }
                for rule in created_rules
            ]
        }
        
    except Exception as e:
        logger.error(f"Failed to seed detection rules: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "internal_error",
                "message": "Failed to seed detection rules"
            }
        )


@router.get("/detections/rules", response_model=List[DetectionRuleSchema])
async def get_detection_rules(
    enabled_only: bool = True,
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve detection rules.
    
    Args:
        enabled_only: If True, only return enabled rules
        db: Database session
        
    Returns:
        List of detection rules
    """
    try:
        if enabled_only:
            rules = await DetectionService.get_enabled_rules(db)
        else:
            # Get all rules (would need to implement this in service)
            rules = await DetectionService.get_enabled_rules(db)
        
        return [DetectionService.detection_rule_to_schema(rule) for rule in rules]
        
    except Exception as e:
        logger.error(f"Error retrieving detection rules: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "internal_error",
                "message": "Failed to retrieve detection rules"
            }
        )


@router.get("/detections/event/{event_id}", response_model=List[DetectionSchema])
async def get_detections_for_event(
    event_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve all detections for a specific event.
    
    Args:
        event_id: Event ID to retrieve detections for
        db: Database session
        
    Returns:
        List of detections for the event
    """
    try:
        detections = await DetectionService.get_detections_by_event(db, event_id)
        
        return [DetectionService.detection_to_schema(detection) for detection in detections]
        
    except Exception as e:
        logger.error(f"Error retrieving detections for event {event_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "internal_error",
                "message": "Failed to retrieve detections"
            }
        )