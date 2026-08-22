from typing import Dict, Any, Optional, Callable
import logging
import asyncio
from datetime import datetime, timedelta
from functools import wraps
from collections import defaultdict

from app.ai.provider_interface import (
    AIProviderError,
    AIProviderTimeoutError,
    AIProviderRateLimitError,
    AIProviderAuthenticationError,
    AIProviderInvalidResponseError,
    AIProviderNetworkError
)

logger = logging.getLogger(__name__)


class CircuitBreaker:
    """Circuit breaker to prevent cascading failures when AI provider is experiencing issues."""
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        expected_exception: Exception = AIProviderError
    ):
        """
        Initialize circuit breaker.
        
        Args:
            failure_threshold: Number of failures before opening circuit
            recovery_timeout: Seconds to wait before attempting recovery
            expected_exception: Exception type to track
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        
        self.failure_count = 0
        self.last_failure_time = None
        self.is_open = False
        self.recovery_start_time = None
        
    def record_success(self):
        """Record a successful call."""
        self.failure_count = 0
        self.is_open = False
        self.recovery_start_time = None
        logger.debug("Circuit breaker: success recorded, circuit closed")
    
    def record_failure(self):
        """Record a failed call."""
        self.failure_count += 1
        self.last_failure_time = datetime.utcnow()
        
        if self.failure_count >= self.failure_threshold:
            self.is_open = True
            self.recovery_start_time = datetime.utcnow()
            logger.warning(f"Circuit breaker: opened after {self.failure_count} failures")
    
    def can_attempt(self) -> bool:
        """
        Check if a call can be attempted.
        
        Returns:
            True if circuit is closed or recovery timeout has passed
        """
        if not self.is_open:
            return True
        
        if self.recovery_start_time:
            elapsed = (datetime.utcnow() - self.recovery_start_time).total_seconds()
            if elapsed >= self.recovery_timeout:
                logger.info("Circuit breaker: recovery timeout elapsed, attempting reset")
                self.is_open = False
                self.failure_count = 0
                self.recovery_start_time = None
                return True
        
        return False
    
    def get_state(self) -> Dict[str, Any]:
        """
        Get current circuit breaker state.
        
        Returns:
            Dictionary with circuit breaker state information
        """
        return {
            "is_open": self.is_open,
            "failure_count": self.failure_count,
            "last_failure_time": self.last_failure_time.isoformat() if self.last_failure_time else None,
            "recovery_start_time": self.recovery_start_time.isoformat() if self.recovery_start_time else None,
            "recovery_timeout": self.recovery_timeout
        }


class AIErrorHandler:
    """Comprehensive error handler for AI provider failures."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize AI error handler.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.enable_circuit_breaker = self.config.get("enable_circuit_breaker", True)
        self.enable_rate_limiting = self.config.get("enable_rate_limiting", True)
        self.enable_fallback = self.config.get("enable_fallback", False)
        
        # Initialize circuit breaker
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=self.config.get("circuit_breaker_threshold", 5),
            recovery_timeout=self.config.get("circuit_breaker_timeout", 60)
        )
        
        # Error statistics
        self.error_stats = defaultdict(int)
        self.total_calls = 0
        self.successful_calls = 0
        
    async def handle_ai_call(
        self,
        call_func: Callable,
        *args,
        **kwargs
    ) -> Any:
        """
        Handle AI provider call with comprehensive error handling.
        
        Args:
            call_func: Async function to call
            *args: Positional arguments for the function
            **kwargs: Keyword arguments for the function
            
        Returns:
            Result from the function call
            
        Raises:
            AIProviderError: If call fails and no fallback available
        """
        self.total_calls += 1
        
        # Check circuit breaker
        if self.enable_circuit_breaker and not self.circuit_breaker.can_attempt():
            logger.warning("Circuit breaker is open, blocking AI call")
            self.error_stats["circuit_breaker_open"] += 1
            raise AIProviderError("Circuit breaker is open, AI provider may be experiencing issues")
        
        try:
            result = await call_func(*args, **kwargs)
            
            # Record success
            self.successful_calls += 1
            if self.enable_circuit_breaker:
                self.circuit_breaker.record_success()
            
            return result
            
        except AIProviderTimeoutError as e:
            self.error_stats["timeout"] += 1
            logger.error(f"AI provider timeout: {str(e)}")
            if self.enable_circuit_breaker:
                self.circuit_breaker.record_failure()
            raise
            
        except AIProviderRateLimitError as e:
            self.error_stats["rate_limit"] += 1
            logger.error(f"AI provider rate limit: {str(e)}")
            if self.enable_circuit_breaker:
                self.circuit_breaker.record_failure()
            raise
            
        except AIProviderAuthenticationError as e:
            self.error_stats["authentication"] += 1
            logger.error(f"AI provider authentication error: {str(e)}")
            # Don't use circuit breaker for auth errors (configuration issue)
            raise
            
        except AIProviderNetworkError as e:
            self.error_stats["network"] += 1
            logger.error(f"AI provider network error: {str(e)}")
            if self.enable_circuit_breaker:
                self.circuit_breaker.record_failure()
            raise
            
        except AIProviderInvalidResponseError as e:
            self.error_stats["invalid_response"] += 1
            logger.error(f"AI provider invalid response: {str(e)}")
            if self.enable_circuit_breaker:
                self.circuit_breaker.record_failure()
            raise
            
        except AIProviderError as e:
            self.error_stats["general"] += 1
            logger.error(f"AI provider error: {str(e)}")
            if self.enable_circuit_breaker:
                self.circuit_breaker.record_failure()
            raise
            
        except Exception as e:
            self.error_stats["unexpected"] += 1
            logger.error(f"Unexpected error during AI call: {str(e)}")
            raise AIProviderError(f"Unexpected error: {str(e)}")
    
    def get_error_stats(self) -> Dict[str, Any]:
        """
        Get error statistics.
        
        Returns:
            Dictionary with error statistics
        """
        return {
            "total_calls": self.total_calls,
            "successful_calls": self.successful_calls,
            "failed_calls": self.total_calls - self.successful_calls,
            "success_rate": self.successful_calls / self.total_calls if self.total_calls > 0 else 0,
            "error_breakdown": dict(self.error_stats),
            "circuit_breaker_state": self.circuit_breaker.get_state() if self.enable_circuit_breaker else None
        }
    
    def reset_stats(self):
        """Reset error statistics."""
        self.error_stats = defaultdict(int)
        self.total_calls = 0
        self.successful_calls = 0
        if self.enable_circuit_breaker:
            self.circuit_breaker = CircuitBreaker(
                failure_threshold=self.config.get("circuit_breaker_threshold", 5),
                recovery_timeout=self.config.get("circuit_breaker_timeout", 60)
            )


def with_error_handling(error_handler: AIErrorHandler):
    """
    Decorator for adding error handling to async functions.
    
    Args:
        error_handler: AIErrorHandler instance
        
    Returns:
        Decorated function
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await error_handler.handle_ai_call(func, *args, **kwargs)
        return wrapper
    return decorator