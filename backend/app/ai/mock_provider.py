from typing import Dict, Any, List, Optional
import asyncio
import logging
from datetime import datetime

from app.ai.provider_interface import (
    AIProviderInterface,
    AIProviderError,
    AIProviderTimeoutError,
    AIProviderRateLimitError,
    AIProviderAuthenticationError,
    AIProviderInvalidResponseError,
    AIProviderNetworkError
)

logger = logging.getLogger(__name__)


class MockAIProvider(AIProviderInterface):
    """Mock AI provider for testing and reference implementation."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the mock AI provider.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.analysis_count = 0
        self.simulate_delay = self.config.get("simulate_delay", 0)
        self.simulate_failure = self.config.get("simulate_failure", False)
        self.simulate_timeout = self.config.get("simulate_timeout", False)
        self.simulate_rate_limit = self.config.get("simulate_rate_limit", False)
        
    async def analyze_finding(
        self,
        finding_data: Dict[str, Any],
        evidence_data: List[Dict[str, Any]],
        detection_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Analyze a finding using mock AI logic.
        
        Args:
            finding_data: Finding information
            evidence_data: List of evidence items
            detection_data: Optional detection information
            
        Returns:
            Structured mock analysis result
            
        Raises:
            AIProviderError: If configured to simulate failure
            AIProviderTimeoutError: If configured to simulate timeout
            AIProviderRateLimitError: If configured to simulate rate limit
        """
        self.analysis_count += 1
        
        # Simulate network delay if configured
        if self.simulate_delay > 0:
            await asyncio.sleep(self.simulate_delay)
        
        # Simulate timeout if configured
        if self.simulate_timeout:
            await asyncio.sleep(30)  # Long delay to simulate timeout
            raise AIProviderTimeoutError("Mock provider timeout")
        
        # Simulate rate limit if configured
        if self.simulate_rate_limit and self.analysis_count > 3:
            raise AIProviderRateLimitError("Mock provider rate limit exceeded")
        
        # Simulate general failure if configured
        if self.simulate_failure:
            raise AIProviderError("Mock provider failure")
        
        # Generate mock analysis based on finding data
        severity = finding_data.get("severity", "UNKNOWN")
        confidence = finding_data.get("confidence", 0)
        title = finding_data.get("title", "Unknown Finding")
        
        # Generate analysis based on severity
        if severity == "CRITICAL":
            risk_level = "HIGH"
            urgency = "IMMEDIATE"
            investigation_priority = "P0"
        elif severity == "HIGH":
            risk_level = "HIGH"
            urgency = "HIGH"
            investigation_priority = "P1"
        elif severity == "MEDIUM":
            risk_level = "MEDIUM"
            urgency = "MEDIUM"
            investigation_priority = "P2"
        else:
            risk_level = "LOW"
            urgency = "LOW"
            investigation_priority = "P3"
        
        # Generate mock indicators based on evidence
        indicators = []
        for evidence in evidence_data[:3]:  # Use first 3 evidence items
            evidence_type = evidence.get("evidence_type", "unknown")
            indicators.append({
                "type": evidence_type,
                "description": f"Indicator from {evidence_type}",
                "confidence": min(100, confidence + 10)
            })
        
        # If no evidence, add generic indicators
        if not indicators:
            indicators.append({
                "type": "detection_trigger",
                "description": "Rule-based detection triggered",
                "confidence": confidence
            })
        
        # Generate mock analysis result
        analysis_result = {
            "summary": f"Analysis of {title}",
            "observed_indicators": indicators,
            "possible_interpretation": self._generate_interpretation(severity, confidence),
            "recommended_investigation_steps": self._generate_investigation_steps(severity),
            "confidence_notes": f"Analysis confidence based on {confidence}% detection confidence",
            "risk_level": risk_level,
            "urgency": urgency,
            "investigation_priority": investigation_priority,
            "analysis_timestamp": datetime.utcnow().isoformat(),
            "provider_metadata": {
                "analysis_count": self.analysis_count,
                "mock_provider": True
            }
        }
        
        logger.info(f"Mock AI analysis completed for finding {finding_data.get('id')}")
        return analysis_result
    
    def _generate_interpretation(self, severity: str, confidence: int) -> str:
        """Generate a mock interpretation based on severity and confidence."""
        if severity == "CRITICAL":
            return "Critical severity finding requires immediate investigation. High confidence indicates reliable detection."
        elif severity == "HIGH":
            return "High severity finding with significant security implications. Confidence level suggests reliable detection."
        elif severity == "MEDIUM":
            return "Medium severity finding with potential security impact. Further investigation recommended."
        else:
            return "Low severity finding with minimal immediate security impact. Monitor for related activity."
    
    def _generate_investigation_steps(self, severity: str) -> List[str]:
        """Generate mock investigation steps based on severity."""
        base_steps = [
            "Review the detection rule that triggered this finding",
            "Examine the associated evidence and events",
            "Correlate with other security events in the same timeframe"
        ]
        
        if severity in ["CRITICAL", "HIGH"]:
            additional_steps = [
                "Check for immediate active threats or compromises",
                "Review user account activity around the detection time",
                "Examine network connections from the source"
            ]
        else:
            additional_steps = [
                "Determine if this is part of a larger pattern",
                "Consider context and baseline behavior"
            ]
        
        return base_steps + additional_steps
    
    def get_provider_name(self) -> str:
        """Return the provider name."""
        return "mock"
    
    def get_model_name(self) -> str:
        """Return the model name."""
        return "mock-model-v1"
    
    def get_version(self) -> str:
        """Return the provider version."""
        return "1.0.0"
