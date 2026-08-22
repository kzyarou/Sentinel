from typing import Dict, Any, List, Optional
import logging
from datetime import datetime

from sqlalchemy.orm import Session

from app.ai.provider_interface import (
    AIProviderInterface,
    AIProviderError,
    AIProviderTimeoutError,
    AIProviderRateLimitError,
    AIProviderAuthenticationError,
    AIProviderInvalidResponseError,
    AIProviderNetworkError
)
from app.ai.prompt_constructor import PromptConstructor
from app.ai.response_validator import ResponseValidator
from app.models.finding import Finding
from app.models.evidence import Evidence
from app.models.detection import Detection
from app.models.ai_analysis import AIAnalysis

logger = logging.getLogger(__name__)


class AIAnalysisService:
    """Service for coordinating AI analysis of findings."""
    
    def __init__(
        self,
        ai_provider: AIProviderInterface,
        prompt_constructor: Optional[PromptConstructor] = None,
        response_validator: Optional[ResponseValidator] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the AI analysis service.
        
        Args:
            ai_provider: AI provider instance
            prompt_constructor: Optional prompt constructor (creates default if not provided)
            response_validator: Optional response validator (creates default if not provided)
            config: Optional configuration dictionary
        """
        self.ai_provider = ai_provider
        self.prompt_constructor = prompt_constructor or PromptConstructor(config)
        self.response_validator = response_validator or ResponseValidator(config)
        self.config = config or {}
        self.enable_analysis = self.config.get("enable_analysis", True)
        self.max_retries = self.config.get("max_retries", 2)
        
    async def analyze_finding(
        self,
        db: Session,
        finding_id: int,
        force_refresh: bool = False
    ) -> AIAnalysis:
        """
        Analyze a finding using AI.
        
        Args:
            db: Database session
            finding_id: ID of the finding to analyze
            force_refresh: Force re-analysis even if recent analysis exists
            
        Returns:
            AIAnalysis model instance
            
        Raises:
            ValueError: If finding not found or analysis disabled
            AIProviderError: If AI analysis fails
        """
        if not self.enable_analysis:
            raise ValueError("AI analysis is disabled")
        
        logger.info(f"Starting AI analysis for finding {finding_id}")
        
        # Fetch finding with related data
        finding = db.query(Finding).filter(Finding.id == finding_id).first()
        if not finding:
            raise ValueError(f"Finding {finding_id} not found")
        
        # Check if recent analysis exists
        if not force_refresh:
            existing_analysis = db.query(AIAnalysis).filter(
                AIAnalysis.finding_id == finding_id
            ).order_by(AIAnalysis.created_at.desc()).first()
            
            if existing_analysis and self._is_analysis_fresh(existing_analysis):
                logger.info(f"Using existing fresh analysis for finding {finding_id}")
                return existing_analysis
        
        # Prepare data for analysis
        finding_data = self._prepare_finding_data(finding)
        evidence_data = self._prepare_evidence_data(db, finding)
        detection_data = self._prepare_detection_data(db, finding)
        
        # Construct prompt
        try:
            prompt = self.prompt_constructor.construct_analysis_prompt(
                finding_data,
                evidence_data,
                detection_data
            )
        except ValueError as e:
            logger.error(f"Prompt construction failed for finding {finding_id}: {str(e)}")
            raise
        
        # Call AI provider with retries
        analysis_result = await self._call_ai_provider_with_retry(
            finding_data,
            evidence_data,
            detection_data
        )
        
        # Validate response
        try:
            validated_result = self.response_validator.validate_analysis_response(analysis_result)
        except ValueError as e:
            logger.error(f"Response validation failed for finding {finding_id}: {str(e)}")
            raise
        
        # Create and persist AI analysis
        ai_analysis = self._create_ai_analysis(
            db,
            finding_id,
            validated_result
        )
        
        logger.info(f"AI analysis completed successfully for finding {finding_id}")
        return ai_analysis
    
    def _prepare_finding_data(self, finding: Finding) -> Dict[str, Any]:
        """
        Prepare finding data for analysis.
        
        Args:
            finding: Finding model instance
            
        Returns:
            Dictionary of finding data
        """
        return {
            "id": finding.id,
            "title": finding.title,
            "description": finding.description,
            "severity": finding.severity,
            "confidence": finding.confidence,
            "status": finding.status,
            "created_at": finding.created_at.isoformat() if finding.created_at else None,
            "metadata": finding.metadata
        }
    
    def _prepare_evidence_data(self, db: Session, finding: Finding) -> List[Dict[str, Any]]:
        """
        Prepare evidence data for analysis.
        
        Args:
            db: Database session
            finding: Finding model instance
            
        Returns:
            List of evidence data dictionaries
        """
        evidence_list = []
        
        # Get evidence through detection relationship
        for detection in finding.detections:
            for evidence in detection.evidence:
                evidence_list.append({
                    "id": evidence.id,
                    "evidence_type": evidence.evidence_type,
                    "description": evidence.description,
                    "source": evidence.source,
                    "confidence": evidence.confidence,
                    "metadata": evidence.metadata
                })
        
        return evidence_list
    
    def _prepare_detection_data(self, db: Session, finding: Finding) -> Optional[Dict[str, Any]]:
        """
        Prepare detection data for analysis.
        
        Args:
            db: Database session
            finding: Finding model instance
            
        Returns:
            Detection data dictionary or None
        """
        if not finding.detections:
            return None
        
        # Use the first detection for analysis
        detection = finding.detections[0]
        return {
            "id": detection.id,
            "rule_name": detection.rule.name if detection.rule else "Unknown",
            "description": detection.description,
            "detected_at": detection.detected_at.isoformat() if detection.detected_at else None,
            "confidence": detection.confidence,
            "metadata": detection.metadata
        }
    
    async def _call_ai_provider_with_retry(
        self,
        finding_data: Dict[str, Any],
        evidence_data: List[Dict[str, Any]],
        detection_data: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Call AI provider with retry logic.
        
        Args:
            finding_data: Finding data
            evidence_data: Evidence data
            detection_data: Detection data
            
        Returns:
            Analysis result from AI provider
            
        Raises:
            AIProviderError: If all retries fail
        """
        last_error = None
        
        for attempt in range(self.max_retries + 1):
            try:
                if attempt > 0:
                    logger.info(f"Retry attempt {attempt} for AI analysis")
                
                result = await self.ai_provider.analyze_finding(
                    finding_data,
                    evidence_data,
                    detection_data
                )
                
                return result
                
            except AIProviderTimeoutError as e:
                last_error = e
                logger.warning(f"AI provider timeout on attempt {attempt + 1}")
                # Retry timeouts
                continue
                
            except AIProviderRateLimitError as e:
                last_error = e
                logger.warning(f"AI provider rate limit on attempt {attempt + 1}")
                # Don't retry rate limits
                raise
                
            except AIProviderAuthenticationError as e:
                last_error = e
                logger.error(f"AI provider authentication error: {str(e)}")
                # Don't retry authentication errors
                raise
                
            except AIProviderNetworkError as e:
                last_error = e
                logger.warning(f"AI provider network error on attempt {attempt + 1}")
                # Retry network errors
                continue
                
            except AIProviderError as e:
                last_error = e
                logger.warning(f"AI provider error on attempt {attempt + 1}: {str(e)}")
                # Retry general errors
                continue
        
        # All retries failed
        raise AIProviderError(f"AI analysis failed after {self.max_retries + 1} attempts: {str(last_error)}")
    
    def _create_ai_analysis(
        self,
        db: Session,
        finding_id: int,
        analysis_result: Dict[str, Any]
    ) -> AIAnalysis:
        """
        Create and persist AI analysis.
        
        Args:
            db: Database session
            finding_id: Finding ID
            analysis_result: Validated analysis result
            
        Returns:
            AIAnalysis model instance
        """
        ai_analysis = AIAnalysis(
            finding_id=finding_id,
            provider_name=self.ai_provider.get_provider_name(),
            model_name=self.ai_provider.get_model_name(),
            model_version=self.ai_provider.get_version(),
            summary=analysis_result.get("summary"),
            observed_indicators=analysis_result.get("observed_indicators", []),
            possible_interpretation=analysis_result.get("possible_interpretation"),
            recommended_investigation_steps=analysis_result.get("recommended_investigation_steps", []),
            confidence_notes=analysis_result.get("confidence_notes"),
            risk_level=analysis_result.get("risk_level"),
            urgency=analysis_result.get("urgency"),
            investigation_priority=analysis_result.get("investigation_priority"),
            metadata={
                "validation_timestamp": analysis_result.get("validation_timestamp"),
                "validation_version": analysis_result.get("validation_version"),
                "provider_metadata": analysis_result.get("provider_metadata", {})
            }
        )
        
        db.add(ai_analysis)
        db.commit()
        db.refresh(ai_analysis)
        
        return ai_analysis
    
    def _is_analysis_fresh(self, analysis: AIAnalysis) -> bool:
        """
        Check if an analysis is still fresh (not stale).
        
        Args:
            analysis: AIAnalysis instance
            
        Returns:
            True if analysis is fresh, False otherwise
        """
        freshness_hours = self.config.get("analysis_freshness_hours", 24)
        
        if not analysis.created_at:
            return False
        
        age = datetime.utcnow() - analysis.created_at
        return age.total_seconds() < (freshness_hours * 3600)
    
    def get_analysis_for_finding(self, db: Session, finding_id: int) -> Optional[AIAnalysis]:
        """
        Get the most recent analysis for a finding.
        
        Args:
            db: Database session
            finding_id: Finding ID
            
        Returns:
            AIAnalysis instance or None
        """
        return db.query(AIAnalysis).filter(
            AIAnalysis.finding_id == finding_id
        ).order_by(AIAnalysis.created_at.desc()).first()