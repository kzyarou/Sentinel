from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.detection_rule import DetectionRule
from app.schemas.detection_rule import DetectionRuleCreate
from app.services.detection_service import DetectionService
import logging

logger = logging.getLogger(__name__)


class RuleSeeds:
    """Seed data for initial detection rules."""
    
    @staticmethod
    def get_initial_rules() -> List[DetectionRuleCreate]:
        """
        Get the initial set of detection rules to seed.
        
        Returns:
            List of DetectionRuleCreate objects for initial rules
        """
        return [
            # Rule 001: Repeated Authentication Failures
            DetectionRuleCreate(
                name="AUTH-BRUTEFORCE",
                description="Detect repeated authentication failures associated with the same user or source within a defined time window",
                category="authentication",
                severity="HIGH",
                version="1",
                enabled=True,
                rule_definition={
                    "failure_threshold": 5,
                    "time_window_minutes": 5,
                    "track_by": "user",
                    "description": "Triggers when 5+ auth failures occur for same user within 5 minutes"
                }
            ),
            
            # Rule 002: Suspicious Privileged Action
            DetectionRuleCreate(
                name="PRIVILEGED-ACTION",
                description="Detect a configured privileged action occurring under conditions defined by the rule",
                category="privilege_escalation",
                severity="HIGH",
                version="1",
                enabled=True,
                rule_definition={
                    "privileged_actions": [
                        "sudo_command",
                        "user_modification",
                        "group_modification",
                        "service_restart",
                        "system_configuration_change"
                    ],
                    "require_elevation": True,
                    "suspicious_conditions": {
                        "outside_business_hours": False,
                        "from_unusual_location": False
                    },
                    "description": "Monitors for elevated privileged actions that may indicate compromise"
                }
            ),
            
            # Rule 003: Unusual Authentication Source
            DetectionRuleCreate(
                name="UNUSUAL-AUTH-SOURCE",
                description="Detect authentication activity from a source that violates a defined rule condition",
                category="authentication",
                severity="MEDIUM",
                version="1",
                enabled=True,
                rule_definition={
                    "trusted_sources": [
                        "192.168.1.0/24",
                        "10.0.0.0/8",
                        "172.16.0.0/12"
                    ],
                    "blocked_sources": [
                        "0.0.0.0/8",  # Invalid source addresses
                        "127.0.0.0/8"  # Loopback (shouldn't come from network)
                    ],
                    "check_geoip": False,
                    "unusual_countries": [],
                    "description": "Detects authentication from untrusted or blocked source IPs"
                }
            )
        ]
    
    @staticmethod
    async def seed_initial_rules(db: AsyncSession) -> List[DetectionRule]:
        """
        Seed the database with initial detection rules.
        
        Args:
            db: Database session
            
        Returns:
            List of created DetectionRule objects
        """
        created_rules = []
        initial_rules = RuleSeeds.get_initial_rules()
        
        for rule_data in initial_rules:
            try:
                # Check if rule already exists
                existing_rule = await DetectionService.get_detection_rule_by_name(
                    db, rule_data.name
                )
                
                if existing_rule:
                    logger.info(f"Rule {rule_data.name} already exists, skipping")
                    created_rules.append(existing_rule)
                    continue
                
                # Create the rule
                created_rule = await DetectionService.create_detection_rule(
                    db, rule_data
                )
                created_rules.append(created_rule)
                logger.info(f"Seeded rule: {created_rule.name} v{created_rule.version}")
                
            except Exception as e:
                logger.error(f"Failed to seed rule {rule_data.name}: {str(e)}")
                # Continue with other rules even if one fails
        
        logger.info(f"Seeded {len(created_rules)} detection rules")
        return created_rules
    
    @staticmethod
    async def update_rule_version(
        db: AsyncSession,
        rule_name: str,
        new_version: str,
        updated_definition: Dict[str, Any]
    ) -> DetectionRule:
        """
        Update an existing rule to a new version.
        
        Args:
            db: Database session
            rule_name: Name of the rule to update
            new_version: New version string
            updated_definition: Updated rule definition
            
        Returns:
            Updated DetectionRule object
        """
        try:
            # Get existing rule
            existing_rule = await DetectionService.get_detection_rule_by_name(
                db, rule_name
            )
            
            if not existing_rule:
                raise ValueError(f"Rule {rule_name} not found")
            
            # Create new version
            updated_rule_data = DetectionRuleCreate(
                name=rule_name,
                description=existing_rule.description,
                category=existing_rule.category,
                severity=existing_rule.severity,
                version=new_version,
                enabled=existing_rule.enabled,
                rule_definition=updated_definition
            )
            
            # Disable old version
            existing_rule.enabled = False
            await db.commit()
            
            # Create new version
            new_rule = await DetectionService.create_detection_rule(
                db, updated_rule_data
            )
            
            logger.info(
                f"Updated rule {rule_name} from v{existing_rule.version} "
                f"to v{new_version}"
            )
            
            return new_rule
            
        except Exception as e:
            logger.error(f"Failed to update rule {rule_name}: {str(e)}")
            raise