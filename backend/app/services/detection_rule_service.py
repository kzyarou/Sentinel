from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from datetime import datetime, timezone
import uuid

from app.models.detection_rule import DetectionRule
from app.schemas.detection_rule import DetectionRuleCreate, DetectionRuleUpdate
from app.services.rule_validation import RuleValidator, RuleValidationError
from app.services.audit_service import AuditService


class DetectionRuleService:
    """Service for managing detection rules."""
    
    def __init__(self, db: AsyncSession, audit_service: AuditService):
        self.db = db
        self.audit_service = audit_service
    
    async def create_rule(
        self, 
        rule_data: DetectionRuleCreate, 
        user_id: Optional[str] = None
    ) -> DetectionRule:
        """Create a new detection rule."""
        # Validate the rule before creation
        RuleValidator.validate_rule_create(rule_data)
        
        # Check if rule with same name and version already exists
        existing_rule = await self.db.execute(
            select(DetectionRule).where(
                and_(
                    DetectionRule.name == rule_data.name,
                    DetectionRule.version == rule_data.version
                )
            )
        )
        if existing_rule.scalar_one_or_none():
            raise RuleValidationError(
                f"Rule with name '{rule_data.name}' and version '{rule_data.version}' already exists",
                field="name"
            )
        
        # Create the rule
        rule = DetectionRule(
            id=str(uuid.uuid4()),
            name=rule_data.name,
            description=rule_data.description,
            category=rule_data.category.value,
            severity=rule_data.severity.value,
            version=rule_data.version,
            enabled=rule_data.enabled,
            rule_definition=rule_data.rule_definition,
            created_by=user_id,
            updated_by=user_id
        )
        
        self.db.add(rule)
        await self.db.commit()
        await self.db.refresh(rule)
        
        # Log audit event
        await self.audit_service.log_detection_rule_created(
            rule_id=rule.id,
            rule_name=rule.name,
            rule_version=rule.version,
            user_id=user_id
        )
        
        return rule
    
    async def get_rule(self, rule_id: str) -> Optional[DetectionRule]:
        """Get a detection rule by ID."""
        result = await self.db.execute(
            select(DetectionRule).where(DetectionRule.id == rule_id)
        )
        return result.scalar_one_or_none()
    
    async def get_rules(
        self,
        skip: int = 0,
        limit: int = 100,
        category: Optional[str] = None,
        severity: Optional[str] = None,
        enabled: Optional[bool] = None,
        search: Optional[str] = None
    ) -> tuple[List[DetectionRule], int]:
        """Get detection rules with filtering and pagination."""
        query = select(DetectionRule)
        
        # Build filters
        conditions = []
        if category:
            conditions.append(DetectionRule.category == category)
        if severity:
            conditions.append(DetectionRule.severity == severity)
        if enabled is not None:
            conditions.append(DetectionRule.enabled == enabled)
        if search:
            conditions.append(
                or_(
                    DetectionRule.name.ilike(f"%{search}%"),
                    DetectionRule.description.ilike(f"%{search}%")
                )
            )
        
        if conditions:
            query = query.where(and_(*conditions))
        
        # Get total count
        count_query = select(DetectionRule.id)
        if conditions:
            count_query = count_query.where(and_(*conditions))
        total_result = await self.db.execute(count_query)
        total = len(total_result.scalars().all())
        
        # Apply pagination and ordering
        query = query.order_by(DetectionRule.name, DetectionRule.version)
        query = query.offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        rules = result.scalars().all()
        
        return list(rules), total
    
    async def update_rule(
        self,
        rule_id: str,
        rule_data: DetectionRuleUpdate,
        user_id: Optional[str] = None
    ) -> Optional[DetectionRule]:
        """Update a detection rule."""
        # Validate the update
        RuleValidator.validate_rule_update(rule_data)
        
        # Get existing rule
        rule = await self.get_rule(rule_id)
        if not rule:
            return None
        
        # Track changes for audit
        changes = []
        
        # Update fields
        if rule_data.description is not None:
            if rule.description != rule_data.description:
                changes.append("description")
            rule.description = rule_data.description
        
        if rule_data.category is not None:
            if rule.category != rule_data.category.value:
                changes.append("category")
            rule.category = rule_data.category.value
        
        if rule_data.severity is not None:
            if rule.severity != rule_data.severity.value:
                changes.append("severity")
            rule.severity = rule_data.severity.value
        
        if rule_data.enabled is not None:
            if rule.enabled != rule_data.enabled:
                changes.append("enabled")
            rule.enabled = rule_data.enabled
        
        if rule_data.rule_definition is not None:
            if rule.rule_definition != rule_data.rule_definition:
                changes.append("rule_definition")
            rule.rule_definition = rule_data.rule_definition
        
        rule.updated_by = user_id
        rule.updated_timestamp = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(rule)
        
        # Log audit event
        if changes:
            await self.audit_service.log_detection_rule_updated(
                rule_id=rule.id,
                rule_name=rule.name,
                rule_version=rule.version,
                changes=changes,
                user_id=user_id
            )
        
        return rule
    
    async def enable_rule(
        self,
        rule_id: str,
        user_id: Optional[str] = None
    ) -> Optional[DetectionRule]:
        """Enable a detection rule."""
        rule = await self.get_rule(rule_id)
        if not rule:
            return None
        
        if rule.enabled:
            return rule  # Already enabled
        
        rule.enabled = True
        rule.updated_by = user_id
        rule.updated_timestamp = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(rule)
        
        # Log audit event
        await self.audit_service.log_detection_rule_enabled(
            rule_id=rule.id,
            rule_name=rule.name,
            rule_version=rule.version,
            user_id=user_id
        )
        
        return rule
    
    async def disable_rule(
        self,
        rule_id: str,
        user_id: Optional[str] = None
    ) -> Optional[DetectionRule]:
        """Disable a detection rule."""
        rule = await self.get_rule(rule_id)
        if not rule:
            return None
        
        if not rule.enabled:
            return rule  # Already disabled
        
        rule.enabled = False
        rule.updated_by = user_id
        rule.updated_timestamp = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(rule)
        
        # Log audit event
        await self.audit_service.log_detection_rule_disabled(
            rule_id=rule.id,
            rule_name=rule.name,
            rule_version=rule.version,
            user_id=user_id
        )
        
        return rule
    
    async def get_rule_versions(self, rule_name: str) -> List[DetectionRule]:
        """Get all versions of a rule by name."""
        result = await self.db.execute(
            select(DetectionRule)
            .where(DetectionRule.name == rule_name)
            .order_by(DetectionRule.version)
        )
        return list(result.scalars().all())
    
    async def delete_rule(self, rule_id: str, user_id: Optional[str] = None) -> bool:
        """Delete a detection rule (soft delete if it has detections)."""
        rule = await self.get_rule(rule_id)
        if not rule:
            return False
        
        # Check if rule has detections
        if rule.detections:
            # Soft delete by disabling
            rule.enabled = False
            rule.updated_by = user_id
            rule.updated_timestamp = datetime.utcnow()
            
            await self.db.commit()
            
            # Log audit event
            await self.audit_service.log_detection_rule_disabled(
                rule_id=rule.id,
                rule_name=rule.name,
                rule_version=rule.version,
                user_id=user_id,
                reason="Rule has associated detections, disabled instead of deleted"
            )
            
            return True
        
        # Hard delete if no detections
        await self.db.delete(rule)
        await self.db.commit()
        
        # Log audit event
        await self.audit_service.log_detection_rule_deleted(
            rule_id=rule.id,
            rule_name=rule.name,
            rule_version=rule.version,
            user_id=user_id
        )
        
        return True