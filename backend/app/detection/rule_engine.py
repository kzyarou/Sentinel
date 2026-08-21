from typing import List, Dict, Any, Optional, TYPE_CHECKING
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
import logging

from app.models.event import Event
from app.models.detection_rule import DetectionRule
from app.services.detection_service import DetectionService
from app.core.utils import generate_uuid

if TYPE_CHECKING:
    from app.models.detection import Detection as DetectionModel
    from app.models.evidence import Evidence as EvidenceModel

logger = logging.getLogger(__name__)


class RuleEvaluationResult:
    """Result of evaluating a single rule against an event."""
    
    def __init__(
        self,
        matched: bool,
        rule: DetectionRule,
        severity: Optional[str] = None,
        confidence: Optional[float] = None,
        evidence: Optional[List[Dict[str, Any]]] = None,
        error: Optional[str] = None
    ):
        self.matched = matched
        self.rule = rule
        self.severity = severity or rule.severity
        self.confidence = confidence or 0.0
        self.evidence = evidence or []
        self.error = error


class RuleEvaluator:
    """Base class for rule evaluation logic."""
    
    @staticmethod
    def evaluate(event: Event, rule: DetectionRule) -> RuleEvaluationResult:
        """
        Evaluate a single rule against an event.
        
        Args:
            event: The event to evaluate
            rule: The rule to evaluate against
            
        Returns:
            RuleEvaluationResult with match status and details
        """
        try:
            # Check if rule is enabled
            if not rule.enabled:
                logger.debug(f"Rule {rule.name} is disabled, skipping evaluation")
                return RuleEvaluationResult(
                    matched=False,
                    rule=rule,
                    error="Rule is disabled"
                )
            
            # Extract rule definition
            rule_def = rule.rule_definition
            
            if not rule_def:
                logger.error(f"Rule {rule.name} has no definition")
                return RuleEvaluationResult(
                    matched=False,
                    rule=rule,
                    error="Rule has no definition"
                )
            
            # Dispatch to specific evaluator based on rule name
            evaluator_map = {
                "AUTH-BRUTEFORCE": RuleEvaluator._evaluate_auth_bruteforce,
                "PRIVILEGED-ACTION": RuleEvaluator._evaluate_privileged_action,
                "UNUSUAL-AUTH-SOURCE": RuleEvaluator._evaluate_unusual_auth_source,
            }
            
            evaluator = evaluator_map.get(rule.name)
            if not evaluator:
                logger.warning(f"No evaluator implemented for rule: {rule.name}")
                return RuleEvaluationResult(
                    matched=False,
                    rule=rule,
                    error=f"No evaluator implemented for rule: {rule.name}"
                )
            
            logger.debug(f"Evaluating event {event.id} against rule {rule.name} v{rule.version}")
            result = evaluator(event, rule, rule_def)
            
            if result.matched:
                logger.info(
                    f"Rule {rule.name} v{rule.version} matched event {event.id} "
                    f"with confidence {result.confidence:.2f}"
                )
            else:
                logger.debug(f"Rule {rule.name} v{rule.version} did not match event {event.id}")
            
            return result
            
        except Exception as e:
            logger.error(
                f"Error evaluating rule {rule.name} v{rule.version} "
                f"for event {event.id}: {str(e)}",
                exc_info=True
            )
            return RuleEvaluationResult(
                matched=False,
                rule=rule,
                error=f"Rule evaluation failed: {str(e)}"
            )
    
    @staticmethod
    def _evaluate_auth_bruteforce(
        event: Event,
        rule: DetectionRule,
        rule_def: Dict[str, Any]
    ) -> RuleEvaluationResult:
        """
        Evaluate repeated authentication failures.
        
        Rule definition should contain:
        - failure_threshold: Number of failures to trigger (default: 5)
        - time_window_minutes: Time window in minutes (default: 5)
        - track_by: Field to track failures by ('user' or 'source_ip')
        """
        try:
            # Extract rule parameters
            failure_threshold = rule_def.get('failure_threshold', 5)
            time_window_minutes = rule_def.get('time_window_minutes', 5)
            track_by = rule_def.get('track_by', 'user')
            
            logger.debug(
                f"AUTH-BRUTEFORCE: threshold={failure_threshold}, "
                f"window={time_window_minutes}min, track_by={track_by}"
            )
            
            # Check if this is an authentication failure event
            if event.event_type != 'auth_failure':
                logger.debug(f"Event type {event.event_type} does not match auth_failure")
                return RuleEvaluationResult(matched=False, rule=rule)
            
            # Extract tracking field from normalized data
            normalized_data = event.normalized_data or {}
            tracking_value = normalized_data.get(track_by)
            
            if not tracking_value:
                logger.warning(
                    f"AUTH-BRUTEFORCE: Tracking field '{track_by}' not found "
                    f"in event {event.id} data"
                )
                return RuleEvaluationResult(
                    matched=False,
                    rule=rule,
                    error=f"Tracking field '{track_by}' not found in event data"
                )
            
            # In a real implementation, we would query for recent failures
            # For now, we'll use a simplified approach checking event metadata
            event_metadata = normalized_data.get('metadata', {})
            recent_failures = event_metadata.get('recent_failures', 0)
            
            logger.debug(
                f"AUTH-BRUTEFORCE: {tracking_value} has {recent_failures} "
                f"recent failures (threshold: {failure_threshold})"
            )
            
            # Check if threshold is exceeded
            if recent_failures >= failure_threshold:
                # Calculate confidence based on how far over threshold
                confidence = min(1.0, 0.5 + (recent_failures - failure_threshold) * 0.1)
                
                logger.info(
                    f"AUTH-BRUTEFORCE: Threshold exceeded for {tracking_value}: "
                    f"{recent_failures} failures vs {failure_threshold} threshold, "
                    f"confidence={confidence:.2f}"
                )
                
                # Generate evidence
                evidence = [
                    {
                        "type": "auth_failure_count",
                        "description": f"Detected {recent_failures} authentication failures",
                        "tracking_field": track_by,
                        "tracking_value": tracking_value,
                        "threshold": failure_threshold,
                        "time_window_minutes": time_window_minutes
                    },
                    {
                        "type": "event_reference",
                        "event_id": event.id,
                        "timestamp": event.timestamp.isoformat()
                    }
                ]
                
                return RuleEvaluationResult(
                    matched=True,
                    rule=rule,
                    severity=rule.severity,
                    confidence=confidence,
                    evidence=evidence
                )
            
            logger.debug(
                f"AUTH-BRUTEFORCE: Threshold not exceeded for {tracking_value}: "
                f"{recent_failures} failures vs {failure_threshold} threshold"
            )
            return RuleEvaluationResult(matched=False, rule=rule)
            
        except Exception as e:
            logger.error(
                f"Error in AUTH-BRUTEFORCE evaluation for event {event.id}: {str(e)}",
                exc_info=True
            )
            return RuleEvaluationResult(
                matched=False,
                rule=rule,
                error=f"Evaluation error: {str(e)}"
            )
    
    @staticmethod
    def _evaluate_privileged_action(
        event: Event,
        rule: DetectionRule,
        rule_def: Dict[str, Any]
    ) -> RuleEvaluationResult:
        """
        Evaluate suspicious privileged actions.
        
        Rule definition should contain:
        - privileged_actions: List of action types to monitor
        - require_elevation: Whether elevation is required (default: true)
        - suspicious_conditions: Optional conditions that make it suspicious
        """
        try:
            # Extract rule parameters
            privileged_actions = rule_def.get('privileged_actions', [])
            require_elevation = rule_def.get('require_elevation', True)
            suspicious_conditions = rule_def.get('suspicious_conditions', {})
            
            logger.debug(
                f"PRIVILEGED-ACTION: actions={privileged_actions}, "
                f"require_elevation={require_elevation}, "
                f"conditions={list(suspicious_conditions.keys())}"
            )
            
            # Check if this is a privileged action event
            if event.event_type != 'privileged_action':
                logger.debug(f"Event type {event.event_type} does not match privileged_action")
                return RuleEvaluationResult(matched=False, rule=rule)
            
            # Extract action from normalized data
            normalized_data = event.normalized_data or {}
            action = normalized_data.get('action')
            
            if not action:
                logger.warning(f"PRIVILEGED-ACTION: No action found in event {event.id}")
                return RuleEvaluationResult(
                    matched=False,
                    rule=rule,
                    error="No action found in event data"
                )
            
            if action not in privileged_actions:
                logger.debug(
                    f"PRIVILEGED-ACTION: Action '{action}' not in privileged actions list"
                )
                return RuleEvaluationResult(matched=False, rule=rule)
            
            # Check elevation requirement
            if require_elevation:
                is_elevated = normalized_data.get('elevated', False)
                if not is_elevated:
                    logger.debug(
                        f"PRIVILEGED-ACTION: Action '{action}' not elevated "
                        f"but elevation required"
                    )
                    return RuleEvaluationResult(matched=False, rule=rule)
            
            # Check suspicious conditions
            is_suspicious = False
            confidence = 0.7  # Base confidence for privileged actions
            matched_conditions = []
            
            for condition, expected_value in suspicious_conditions.items():
                actual_value = normalized_data.get(condition)
                if actual_value == expected_value:
                    is_suspicious = True
                    confidence += 0.1
                    matched_conditions.append(condition)
                    logger.debug(
                        f"PRIVILEGED-ACTION: Suspicious condition '{condition}' matched"
                    )
            
            # If no suspicious conditions specified, all matching actions are suspicious
            if not suspicious_conditions:
                is_suspicious = True
                logger.debug(
                    f"PRIVILEGED-ACTION: No suspicious conditions specified, "
                    f"treating as suspicious"
                )
            
            if is_suspicious:
                logger.info(
                    f"PRIVILEGED-ACTION: Suspicious privileged action '{action}' detected, "
                    f"elevated={normalized_data.get('elevated', False)}, "
                    f"matched_conditions={matched_conditions}, "
                    f"confidence={confidence:.2f}"
                )
                
                # Generate evidence
                evidence = [
                    {
                        "type": "privileged_action_detected",
                        "description": f"Privileged action '{action}' detected",
                        "action": action,
                        "elevated": normalized_data.get('elevated', False)
                    },
                    {
                        "type": "event_reference",
                        "event_id": event.id,
                        "timestamp": event.timestamp.isoformat()
                    }
                ]
                
                # Add context fields as evidence
                for field in ['user', 'host', 'source_ip']:
                    if field in normalized_data:
                        evidence.append({
                            "type": "context_field",
                            "field": field,
                            "value": normalized_data[field]
                        })
                
                return RuleEvaluationResult(
                    matched=True,
                    rule=rule,
                    severity=rule.severity,
                    confidence=min(1.0, confidence),
                    evidence=evidence
                )
            
            logger.debug(
                f"PRIVILEGED-ACTION: Action '{action}' did not meet suspicious criteria"
            )
            return RuleEvaluationResult(matched=False, rule=rule)
            
        except Exception as e:
            logger.error(
                f"Error in PRIVILEGED-ACTION evaluation for event {event.id}: {str(e)}",
                exc_info=True
            )
            return RuleEvaluationResult(
                matched=False,
                rule=rule,
                error=f"Evaluation error: {str(e)}"
            )
    
    @staticmethod
    def _evaluate_unusual_auth_source(
        event: Event,
        rule: DetectionRule,
        rule_def: Dict[str, Any]
    ) -> RuleEvaluationResult:
        """
        Evaluate unusual authentication sources.
        
        Rule definition should contain:
        - trusted_sources: List of trusted source IPs or ranges
        - blocked_sources: List of blocked source IPs or ranges
        - check_geoip: Whether to check geographic location (default: false)
        - unusual_countries: List of unusual country codes
        """
        try:
            # Extract rule parameters
            trusted_sources = rule_def.get('trusted_sources', [])
            blocked_sources = rule_def.get('blocked_sources', [])
            check_geoip = rule_def.get('check_geoip', False)
            unusual_countries = rule_def.get('unusual_countries', [])
            
            logger.debug(
                f"UNUSUAL-AUTH-SOURCE: trusted={len(trusted_sources)}, "
                f"blocked={len(blocked_sources)}, check_geoip={check_geoip}, "
                f"unusual_countries={unusual_countries}"
            )
            
            # Check if this is an authentication event
            if event.event_type not in ['auth_success', 'auth_failure']:
                logger.debug(
                    f"Event type {event.event_type} does not match auth events"
                )
                return RuleEvaluationResult(matched=False, rule=rule)
            
            # Extract source IP from normalized data
            normalized_data = event.normalized_data or {}
            source_ip = normalized_data.get('source_ip')
            
            if not source_ip:
                logger.warning(
                    f"UNUSUAL-AUTH-SOURCE: Source IP not found in event {event.id}"
                )
                return RuleEvaluationResult(
                    matched=False,
                    rule=rule,
                    error="Source IP not found in event data"
                )
            
            logger.debug(f"UNUSUAL-AUTH-SOURCE: Evaluating source IP {source_ip}")
            
            # Check if source is blocked
            if source_ip in blocked_sources:
                logger.warning(
                    f"UNUSUAL-AUTH-SOURCE: Blocked source IP detected: {source_ip}"
                )
                evidence = [
                    {
                        "type": "blocked_source_detected",
                        "description": f"Authentication from blocked source IP: {source_ip}",
                        "source_ip": source_ip
                    },
                    {
                        "type": "event_reference",
                        "event_id": event.id,
                        "timestamp": event.timestamp.isoformat()
                    }
                ]
                
                return RuleEvaluationResult(
                    matched=True,
                    rule=rule,
                    severity=rule.severity,
                    confidence=1.0,  # High confidence for blocked sources
                    evidence=evidence
                )
            
            # Check if source is not trusted (if trusted list is specified)
            is_unusual = False
            confidence = 0.5
            reasons = []
            
            if trusted_sources and source_ip not in trusted_sources:
                is_unusual = True
                confidence += 0.2
                reasons.append("untrusted_source")
                logger.debug(
                    f"UNUSUAL-AUTH-SOURCE: Source {source_ip} not in trusted list"
                )
            
            # Check geographic location if enabled
            if check_geoip:
                country = normalized_data.get('country')
                if country and country in unusual_countries:
                    is_unusual = True
                    confidence += 0.3
                    reasons.append(f"unusual_country_{country}")
                    logger.warning(
                        f"UNUSUAL-AUTH-SOURCE: Authentication from unusual country: {country}"
                    )
                    evidence = [
                        {
                            "type": "unusual_geo_location",
                            "description": f"Authentication from unusual country: {country}",
                            "country": country,
                            "source_ip": source_ip
                        }
                    ]
                else:
                    evidence = []
            else:
                evidence = []
            
            if is_unusual:
                logger.info(
                    f"UNUSUAL-AUTH-SOURCE: Unusual source detected: {source_ip}, "
                    f"reasons={reasons}, confidence={confidence:.2f}"
                )
                evidence.extend([
                    {
                        "type": "unusual_auth_source",
                        "description": f"Authentication from unusual source: {source_ip}",
                        "source_ip": source_ip,
                        "reasons": reasons
                    },
                    {
                        "type": "event_reference",
                        "event_id": event.id,
                        "timestamp": event.timestamp.isoformat()
                    }
                ])
                
                return RuleEvaluationResult(
                    matched=True,
                    rule=rule,
                    severity=rule.severity,
                    confidence=min(1.0, confidence),
                    evidence=evidence
                )
            
            logger.debug(
                f"UNUSUAL-AUTH-SOURCE: Source {source_ip} appears normal"
            )
            return RuleEvaluationResult(matched=False, rule=rule)
            
        except Exception as e:
            logger.error(
                f"Error in UNUSUAL-AUTH-SOURCE evaluation for event {event.id}: {str(e)}",
                exc_info=True
            )
            return RuleEvaluationResult(
                matched=False,
                rule=rule,
                error=f"Evaluation error: {str(e)}"
            )


class DetectionEngine:
    """Main detection engine for evaluating events against rules."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def evaluate_event(self, event: Event) -> List['DetectionModel']:
        """
        Evaluate an event against all enabled rules.
        
        Args:
            event: The event to evaluate
            db: Database session
            
        Returns:
            List of Detection objects created from matching rules
        """
        detections = []
        
        try:
            # Get all enabled rules
            enabled_rules = await DetectionService.get_enabled_rules(self.db)
            
            if not enabled_rules:
                logger.warning(f"No enabled rules found for event {event.id} evaluation")
                return detections
            
            logger.info(
                f"Evaluating event {event.id} (type: {event.event_type}) "
                f"against {len(enabled_rules)} enabled rules"
            )
            
            # Evaluate against each rule
            for rule in enabled_rules:
                try:
                    result = RuleEvaluator.evaluate(event, rule)
                    
                    if result.error:
                        logger.warning(
                            f"Rule evaluation error for {rule.name} v{rule.version}: "
                            f"{result.error}"
                        )
                        continue
                    
                    if result.matched:
                        # Create detection
                        detection = await self._create_detection_from_result(
                            event, rule, result
                        )
                        detections.append(detection)
                        
                        # Create evidence
                        await self._create_evidence_for_detection(
                            detection, result.evidence, event
                        )
                        
                        logger.info(
                            f"Detection created: {detection.id} "
                            f"from rule {rule.name} v{rule.version} "
                            f"(severity: {result.severity}, confidence: {result.confidence:.2f})"
                        )
                
                except Exception as e:
                    logger.error(
                        f"Error processing rule {rule.name} v{rule.version} "
                        f"for event {event.id}: {str(e)}",
                        exc_info=True
                    )
                    # Continue with other rules even if one fails
            
            logger.info(
                f"Event {event.id} evaluation complete: "
                f"{len(detections)} detections created from {len(enabled_rules)} rules"
            )
            return detections
            
        except Exception as e:
            logger.error(
                f"Error in detection engine for event {event.id}: {str(e)}",
                exc_info=True
            )
            return detections
    
    async def _create_detection_from_result(
        self,
        event: Event,
        rule: DetectionRule,
        result: RuleEvaluationResult
    ) -> 'DetectionModel':
        """Create a detection from an evaluation result."""
        from app.schemas.detection import DetectionCreate as DetectionCreateSchema
        
        detection_data = DetectionCreateSchema(
            detection_rule_id=rule.id,
            event_id=event.id,
            severity=result.severity,
            confidence=int(result.confidence * 100),  # Convert to 0-100 scale
            rule_version=rule.version,
            detection_metadata={
                "rule_name": rule.name,
                "evaluation_timestamp": datetime.utcnow().isoformat()
            }
        )
        
        return await DetectionService.create_detection(self.db, detection_data)
    
    async def _create_evidence_for_detection(
        self,
        detection: 'DetectionModel',
        evidence_items: List[Dict[str, Any]],
        event: Event
    ) -> None:
        """Create evidence items for a detection."""
        from app.schemas.evidence import EvidenceCreate as EvidenceCreateSchema
        
        for evidence_item in evidence_items:
            try:
                evidence_data = EvidenceCreateSchema(
                    detection_id=detection.id,
                    event_id=event.id,
                    evidence_type=evidence_item.get("type", "generic"),
                    evidence_content=evidence_item
                )
                
                await DetectionService.create_evidence(self.db, evidence_data)
                logger.debug(f"Created evidence for detection {detection.id}")
            except Exception as e:
                logger.error(
                    f"Failed to create evidence for detection {detection.id}: {str(e)}",
                    exc_info=True
                )
                # Continue with other evidence items even if one fails