from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
import logging

from app.models.detection import Detection
from app.models.detection_rule import DetectionRule
from app.models.evidence import Evidence
from app.models.event import Event
from app.schemas.detection import DetectionCreate, Detection as DetectionSchema
from app.schemas.detection_rule import DetectionRuleCreate, DetectionRule as DetectionRuleSchema
from app.schemas.evidence import EvidenceCreate, Evidence as EvidenceSchema
from app.core.utils import generate_uuid

logger = logging.getLogger(__name__)


class DetectionService:
    """Service for detection rule management and detection processing."""
    
    @staticmethod
    async def create_detection_rule(
        db: AsyncSession,
        rule_data: DetectionRuleCreate,
        rule_id: Optional[str] = None
    ) -> DetectionRule:
        """
        Create and persist a new detection rule.
        
        Args:
            db: Database session
            rule_data: Validated rule data
            rule_id: Optional rule ID (generates UUID if not provided)
            
        Returns:
            Created DetectionRule object
        """
        if not rule_id:
            rule_id = generate_uuid()
        
        db_rule = DetectionRule(
            id=rule_id,
            name=rule_data.name,
            description=rule_data.description,
            category=rule_data.category,
            severity=rule_data.severity,
            version=rule_data.version,
            enabled=rule_data.enabled,
            rule_definition=rule_data.rule_definition
        )
        
        db.add(db_rule)
        await db.commit()
        await db.refresh(db_rule)
        
        logger.info(f"Detection rule created: {db_rule.name} v{db_rule.version}")
        return db_rule
    
    @staticmethod
    async def get_detection_rule_by_id(db: AsyncSession, rule_id: str) -> Optional[DetectionRule]:
        """
        Retrieve a detection rule by ID.
        
        Args:
            db: Database session
            rule_id: Rule ID to retrieve
            
        Returns:
            DetectionRule object if found, None otherwise
        """
        result = await db.execute(
            select(DetectionRule).where(DetectionRule.id == rule_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_detection_rule_by_name(db: AsyncSession, name: str) -> Optional[DetectionRule]:
        """
        Retrieve a detection rule by name.
        
        Args:
            db: Database session
            name: Rule name to retrieve
            
        Returns:
            DetectionRule object if found, None otherwise
        """
        result = await db.execute(
            select(DetectionRule).where(DetectionRule.name == name)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_enabled_rules(db: AsyncSession) -> List[DetectionRule]:
        """
        Retrieve all enabled detection rules.
        
        Args:
            db: Database session
            
        Returns:
            List of enabled DetectionRule objects
        """
        result = await db.execute(
            select(DetectionRule)
            .where(DetectionRule.enabled == True)
            .order_by(DetectionRule.name, DetectionRule.version)
        )
        return result.scalars().all()
    
    @staticmethod
    async def create_detection(
        db: AsyncSession,
        detection_data: DetectionCreate,
        detection_id: Optional[str] = None
    ) -> Detection:
        """
        Create and persist a new detection.
        
        Args:
            db: Database session
            detection_data: Validated detection data
            detection_id: Optional detection ID (generates UUID if not provided)
            
        Returns:
            Created Detection object
        """
        if not detection_id:
            detection_id = generate_uuid()
        
        db_detection = Detection(
            id=detection_id,
            detection_rule_id=detection_data.detection_rule_id,
            event_id=detection_data.event_id,
            severity=detection_data.severity,
            confidence=detection_data.confidence,
            rule_version=detection_data.rule_version,
            detection_metadata=detection_data.detection_metadata
        )
        
        db.add(db_detection)
        await db.commit()
        await db.refresh(db_detection)
        
        logger.info(f"Detection created: {detection_id} for rule {detection_data.detection_rule_id}")
        return db_detection
    
    @staticmethod
    async def create_evidence(
        db: AsyncSession,
        evidence_data: EvidenceCreate,
        evidence_id: Optional[str] = None
    ) -> Evidence:
        """
        Create and persist evidence for a detection.
        
        Args:
            db: Database session
            evidence_data: Validated evidence data
            evidence_id: Optional evidence ID (generates UUID if not provided)
            
        Returns:
            Created Evidence object
        """
        if not evidence_id:
            evidence_id = generate_uuid()
        
        db_evidence = Evidence(
            id=evidence_id,
            finding_id=evidence_data.finding_id,
            detection_id=evidence_data.detection_id,
            event_id=evidence_data.event_id,
            evidence_type=evidence_data.evidence_type,
            evidence_content=evidence_data.evidence_content
        )
        
        db.add(db_evidence)
        await db.commit()
        await db.refresh(db_evidence)
        
        logger.info(f"Evidence created: {evidence_id} for detection {evidence_data.detection_id}")
        return db_evidence
    
    @staticmethod
    async def get_detections_by_event(db: AsyncSession, event_id: str) -> List[Detection]:
        """
        Retrieve all detections for a specific event.
        
        Args:
            db: Database session
            event_id: Event ID to filter by
            
        Returns:
            List of Detection objects
        """
        result = await db.execute(
            select(Detection)
            .where(Detection.event_id == event_id)
            .order_by(Detection.detection_timestamp.desc())
        )
        return result.scalars().all()
    
    @staticmethod
    async def get_evidence_for_detection(db: AsyncSession, detection_id: str) -> List[Evidence]:
        """
        Retrieve all evidence for a specific detection.
        
        Args:
            db: Database session
            detection_id: Detection ID to filter by
            
        Returns:
            List of Evidence objects
        """
        result = await db.execute(
            select(Evidence)
            .where(Evidence.detection_id == detection_id)
            .order_by(Evidence.created_timestamp.asc())
        )
        return result.scalars().all()
    
    @staticmethod
    def detection_rule_to_schema(rule: DetectionRule) -> DetectionRuleSchema:
        """
        Convert DetectionRule model to DetectionRule schema.
        
        Args:
            rule: DetectionRule model object
            
        Returns:
            DetectionRule schema object
        """
        return DetectionRuleSchema(
            id=rule.id,
            name=rule.name,
            description=rule.description,
            category=rule.category,
            severity=rule.severity,
            version=rule.version,
            enabled=rule.enabled,
            rule_definition=rule.rule_definition,
            created_timestamp=rule.created_timestamp,
            updated_timestamp=rule.updated_timestamp
        )
    
    @staticmethod
    def detection_to_schema(detection: Detection) -> DetectionSchema:
        """
        Convert Detection model to Detection schema.
        
        Args:
            detection: Detection model object
            
        Returns:
            Detection schema object
        """
        return DetectionSchema(
            id=detection.id,
            detection_rule_id=detection.detection_rule_id,
            event_id=detection.event_id,
            severity=detection.severity,
            confidence=detection.confidence,
            rule_version=detection.rule_version,
            detection_metadata=detection.detection_metadata,
            detection_timestamp=detection.detection_timestamp
        )
    
    @staticmethod
    def evidence_to_schema(evidence: Evidence) -> EvidenceSchema:
        """
        Convert Evidence model to Evidence schema.
        
        Args:
            evidence: Evidence model object
            
        Returns:
            Evidence schema object
        """
        return EvidenceSchema(
            id=evidence.id,
            finding_id=evidence.finding_id,
            detection_id=evidence.detection_id,
            event_id=evidence.event_id,
            evidence_type=evidence.evidence_type,
            evidence_content=evidence.evidence_content,
            created_timestamp=evidence.created_timestamp
        )