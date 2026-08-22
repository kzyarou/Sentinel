from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)


class AIProviderInterface(ABC):
    """Abstract interface for AI providers."""
    
    @abstractmethod
    async def analyze_finding(
        self,
        finding_data: Dict[str, Any],
        evidence_data: List[Dict[str, Any]],
        detection_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Analyze a finding using AI.
        
        Args:
            finding_data: Finding information (title, description, severity, confidence, status)
            evidence_data: List of evidence items
            detection_data: Optional detection information
            
        Returns:
            Structured analysis result
            
        Raises:
            AIProviderError: If analysis fails
        """
        pass
    
    @abstractmethod
    def get_provider_name(self) -> str:
        """Return the provider name."""
        pass
    
    @abstractmethod
    def get_model_name(self) -> str:
        """Return the model name."""
        pass
    
    @abstractmethod
    def get_version(self) -> str:
        """Return the provider version."""
        pass


class AIProviderError(Exception):
    """Base exception for AI provider errors."""
    pass


class AIProviderTimeoutError(AIProviderError):
    """Exception raised when AI provider times out."""
    pass


class AIProviderRateLimitError(AIProviderError):
    """Exception raised when AI provider rate limit is exceeded."""
    pass


class AIProviderAuthenticationError(AIProviderError):
    """Exception raised when AI provider authentication fails."""
    pass


class AIProviderInvalidResponseError(AIProviderError):
    """Exception raised when AI provider returns invalid response."""
    pass


class AIProviderNetworkError(AIProviderError):
    """Exception raised when network error occurs with AI provider."""
    pass