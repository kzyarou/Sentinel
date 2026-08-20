from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from datetime import datetime
import logging

from app.models.finding import Finding, FindingStatus
from app.models.detection import Detection
from app.models.evidence import Evidence
from app.schemas.finding import FindingCreate, FindingUpdate, Finding as FindingSchema
from app.core.utils import generate_uuid

logger = logging.getLogger(__name__)


class FindingService:
    """Service for finding management and lifecycle operations."""
    
    # Valid state transitions
    VALID_TRANSITIONS = {
        FindingStatus.OPEN: [FindingStatus.INVESTIGATING, FindingStatus.FALSE_POSITIVE],
        FindingStatus.INVESTIGATING: [FindingStatus.RESOLVED, FindingStatus.FALSE_POSITIVE, FindingStatus.OPEN],
        FindingStatus.RESOLVED: [FindingStatus.OPEN, FindingStatus.INVESTIGATING],
        FindingStatus.FALSE_POSITIVE: [FindingStatus.OPEN, FindingStatus.INVESTIGATING],
    }
    
    @staticmethod
    def is_valid_transition(current_status: FindingStatus, new_status: FindingStatus) -> bool:
        """
        Check if a status transition is valid.
        
        Args:
            current_status: Current finding status
            new_status: Desired new status
            
        Returns:
            True if transition is valid, False otherwise
        """
        if current_status == new_status:
            return True  # No-op transition is valid
        
        valid_next_statuses = FindingService.VALID_TRANSITIONS.get(current_status, [])
        return new_status in valid_next_statuses
    
    @staticmethod
    async def create_finding(
        db: AsyncSession,
        finding_data: FindingCreate,
        finding_id: Optional[str] = None
    ) -> Finding:
        """
        Create and persist a new finding.
        
        Args:
            db: Database session
            finding_data: Validated finding data
            finding_id: Optional finding ID (generates UUID if not provided)
            
        Returns:
            Created Finding object
        """
        if not finding_id:
            finding_id = generate_uuid()
        
        db_finding = Finding(
            id=finding_id,
            title=finding_data.title,
            description=finding_data.description,
            severity=finding_data.severity,
            confidence=finding_data.confidence,
            status=finding_data.status,
            detection_id=finding_data.detection_id,
            finding_metadata=finding_data.finding_metadata
        )
        
        db.add(db_finding)
        await db.commit()
        await db.refresh(db_finding)
        
        logger.info(f"Finding created: {db_finding.id} with status {db_finding.status}")
        return db_finding
    
    @staticmethod
    async def get_finding_by_id(db: AsyncSession, finding_id: str) -> Optional[Finding]:
        """
        Retrieve a finding by ID.
        
        Args:
            db: Database session
            finding_id: Finding ID to retrieve
            
        Returns:
            Finding object if found, None otherwise
        """
        result = await db.execute(
            select(Finding).where(Finding.id == finding_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_findings(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        severity: Optional[str] = None,
        status: Optional[FindingStatus] = None
    ) -> List[Finding]:
        """
        Retrieve findings with optional filtering.
        
        Args:
            db: Database session
            skip: Number of results to skip (pagination)
            limit: Maximum number of results to return
            severity: Optional severity filter
            status: Optional status filter
            
        Returns:
            List of Finding objects
        """
        query = select(Finding)
        
        # Apply filters
        conditions = []
        if severity:
            conditions.append(Finding.severity == severity)
        if status:
            conditions.append(Finding.status == status)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        # Apply ordering and pagination
        query = query.order_by(Finding.created_timestamp.desc())
        query = query.offset(skip).limit(limit)
        
        result = await db.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def update_finding(
        db: AsyncSession,
        finding_id: str,
        finding_update: FindingUpdate
    ) -> Optional[Finding]:
        """
        Update an existing finding.
        
        Args:
            db: Database session
            finding_id: Finding ID to update
            finding_update: Update data
            
        Returns:
            Updated Finding object if found, None otherwise
        """
        db_finding = await FindingService.get_finding_by_id(db, finding_id)
        
        if not db_finding:
            return None
        
        # Validate status transition if status is being updated
        if finding_update.status and finding_update.status != db_finding.status:
            if not FindingService.is_valid_transition(db_finding.status, finding_update.status):
                logger.warning(
                    f"Invalid status transition for finding {finding_id}: "
                    f"{db_finding.status} -> {finding_update.status}"
                )
                raise ValueError(
                    f"Invalid status transition: {db_finding.status} -> {finding_update.status}"
                )
        
        # Update fields
        update_data = finding_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_finding, field, value)
        
        await db.commit()
        await db.refresh(db_finding)
        
        logger.info(f"Finding updated: {finding_id}")
        return db_finding
    
    @staticmethod
    async def delete_finding(db: AsyncSession, finding_id: str) -> bool:
        """
        Delete a finding.
        
        Args:
            db: Database session
            finding_id: Finding ID to delete
            
        Returns:
            True if deleted, False if not found
        """
        db_finding = await FindingService.get_finding_by_id(db, finding_id)
        
        if not db_finding:
            return False
        
        await db.delete(db_finding)
        await db.commit()
        
        logger.info(f"Finding deleted: {finding_id}")
        return True
    
    @staticmethod
    async def get_finding_detection(db: AsyncSession, finding_id: str) -> Optional[Detection]:
        """
        Retrieve the detection associated with a finding.
        
        Args:
            db: Database session
            finding_id: Finding ID
            
        Returns:
            Detection object if found, None otherwise
        """
        finding = await FindingService.get_finding_by_id(db, finding_id)
        
        if not finding or not finding.detection_id:
            return None
        
        result = await db.execute(
            select(Detection).where(Detection.id == finding.detection_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_finding_evidence(db: AsyncSession, finding_id: str) -> List[Evidence]:
        """
        Retrieve all evidence associated with a finding.
        
        Args:
            db: Database session
            finding_id: Finding ID
            
        Returns:
            List of Evidence objects
        """
        result = await db.execute(
            select(Evidence)
            .where(Evidence.finding_id == finding_id)
            .order_by(Evidence.created_timestamp.asc())
        )
        return result.scalars().all()
    
    @staticmethod
    async def create_finding_from_detection(
        db: AsyncSession,
        detection: Detection,
        title_override: Optional[str] = None,
        description_override: Optional[str] = None
    ) -> Finding:
        """
        Create a finding from a detection.
        
        Args:
            db: Database session
            detection: Detection object to convert to finding
            title_override: Optional title override
            description_override: Optional description override
            
        Returns:
            Created Finding object
        """
        # Generate title and description from detection if not provided
        if not title_override:
            title_override = f"{detection.detection_metadata.get('rule_name', 'Unknown Rule')} Detection"
        
        if not description_override:
            description_override = (
                f"Detection created by rule {detection.detection_metadata.get('rule_name', 'Unknown')} "
                f"version {detection.rule_version} with {detection.confidence}% confidence"
            )
        
        # Preserve detection metadata in finding
        finding_metadata = {
            "detection_id": detection.id,
            "rule_name": detection.detection_metadata.get("rule_name"),
            "rule_version": detection.rule_version,
            "detection_timestamp": detection.detection_timestamp.isoformat(),
            "detection_confidence": detection.confidence,
            "detection_severity": detection.severity
        }
        
        finding_data = FindingCreate(
            title=title_override,
            description=description_override,
            severity=detection.severity,
            confidence=detection.confidence,
            status=FindingStatus.OPEN,
            detection_id=detection.id,
            finding_metadata=finding_metadata
        )
        
        finding = await FindingService.create_finding(db, finding_data)
        
        logger.info(
            f"Finding created from detection {detection.id}: "
            f"finding {finding.id}, rule {detection.detection_metadata.get('rule_name')}"
        )
        
        return finding
    
    @staticmethod
    def finding_to_schema(finding: Finding) -> FindingSchema:
        """
        Convert Finding model to Finding schema.
        
        Args:
            finding: Finding model object
            
        Returns:
            Finding schema object
        """
        return FindingSchema(
            id=finding.id,
            title=finding.title,
            description=finding.description,
            severity=finding.severity,
            confidence=finding.confidence,
            status=finding.status,
            detection_id=finding.detection_id,
            finding_metadata=finding.finding_metadata,
            created_timestamp=finding.created_timestamp,
            updated_timestamp=finding.updated_timestamp
        )