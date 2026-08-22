from typing import Dict, Any, List, Optional
import logging
import json
from datetime import datetime

logger = logging.getLogger(__name__)


class ResponseValidator:
    """Service for validating structured AI responses."""
    
    REQUIRED_FIELDS = [
        "summary",
        "observed_indicators",
        "possible_interpretation",
        "recommended_investigation_steps",
        "confidence_notes",
        "risk_level",
        "urgency",
        "investigation_priority"
    ]
    
    VALID_RISK_LEVELS = ["HIGH", "MEDIUM", "LOW"]
    VALID_URGENCY_LEVELS = ["IMMEDIATE", "HIGH", "MEDIUM", "LOW"]
    VALID_PRIORITY_LEVELS = ["P0", "P1", "P2", "P3"]
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the response validator.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.enable_strict_validation = self.config.get("enable_strict_validation", True)
        self.max_response_length = self.config.get("max_response_length", 50000)
        
    def validate_analysis_response(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate AI analysis response structure and content.
        
        Args:
            response_data: Response data from AI provider
            
        Returns:
            Validated and normalized response data
            
        Raises:
            ValueError: If response is invalid
        """
        logger.info("Validating AI analysis response")
        
        # Check response length
        response_str = json.dumps(response_data)
        if len(response_str) > self.max_response_length:
            logger.warning(f"Response length {len(response_str)} exceeds max {self.max_response_length}")
            if self.enable_strict_validation:
                raise ValueError(f"Response exceeds maximum length of {self.max_response_length}")
        
        # Validate required fields
        if self.enable_strict_validation:
            self._validate_required_fields(response_data)
        
        # Validate field types and values
        validated_response = self._validate_field_types(response_data)
        
        # Normalize response
        normalized_response = self._normalize_response(validated_response)
        
        logger.info("AI analysis response validation successful")
        return normalized_response
    
    def _validate_required_fields(self, response_data: Dict[str, Any]) -> None:
        """
        Validate that all required fields are present.
        
        Args:
            response_data: Response data to validate
            
        Raises:
            ValueError: If required fields are missing
        """
        missing_fields = []
        
        for field in self.REQUIRED_FIELDS:
            if field not in response_data:
                missing_fields.append(field)
        
        if missing_fields:
            raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")
    
    def _validate_field_types(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate field types and values.
        
        Args:
            response_data: Response data to validate
            
        Returns:
            Validated response data
            
        Raises:
            ValueError: If field types or values are invalid
        """
        validated = response_data.copy()
        
        # Validate summary (string)
        if "summary" in validated and not isinstance(validated["summary"], str):
            validated["summary"] = str(validated["summary"])
        
        # Validate observed_indicators (list)
        if "observed_indicators" in validated:
            if not isinstance(validated["observed_indicators"], list):
                validated["observed_indicators"] = []
            else:
                validated["observed_indicators"] = [
                    self._validate_indicator(indicator)
                    for indicator in validated["observed_indicators"]
                ]
        
        # Validate possible_interpretation (string)
        if "possible_interpretation" in validated and not isinstance(validated["possible_interpretation"], str):
            validated["possible_interpretation"] = str(validated["possible_interpretation"])
        
        # Validate recommended_investigation_steps (list of strings)
        if "recommended_investigation_steps" in validated:
            if not isinstance(validated["recommended_investigation_steps"], list):
                validated["recommended_investigation_steps"] = []
            else:
                validated["recommended_investigation_steps"] = [
                    str(step) if not isinstance(step, str) else step
                    for step in validated["recommended_investigation_steps"]
                ]
        
        # Validate confidence_notes (string)
        if "confidence_notes" in validated and not isinstance(validated["confidence_notes"], str):
            validated["confidence_notes"] = str(validated["confidence_notes"])
        
        # Validate risk_level
        if "risk_level" in validated:
            if not isinstance(validated["risk_level"], str):
                validated["risk_level"] = str(validated["risk_level"]).upper()
            validated["risk_level"] = validated["risk_level"].upper()
            if self.enable_strict_validation and validated["risk_level"] not in self.VALID_RISK_LEVELS:
                raise ValueError(f"Invalid risk_level: {validated['risk_level']}. Must be one of {self.VALID_RISK_LEVELS}")
        
        # Validate urgency
        if "urgency" in validated:
            if not isinstance(validated["urgency"], str):
                validated["urgency"] = str(validated["urgency"]).upper()
            validated["urgency"] = validated["urgency"].upper()
            if self.enable_strict_validation and validated["urgency"] not in self.VALID_URGENCY_LEVELS:
                raise ValueError(f"Invalid urgency: {validated['urgency']}. Must be one of {self.VALID_URGENCY_LEVELS}")
        
        # Validate investigation_priority
        if "investigation_priority" in validated:
            if not isinstance(validated["investigation_priority"], str):
                validated["investigation_priority"] = str(validated["investigation_priority"]).upper()
            validated["investigation_priority"] = validated["investigation_priority"].upper()
            if self.enable_strict_validation and validated["investigation_priority"] not in self.VALID_PRIORITY_LEVELS:
                raise ValueError(f"Invalid investigation_priority: {validated['investigation_priority']}. Must be one of {self.VALID_PRIORITY_LEVELS}")
        
        return validated
    
    def _validate_indicator(self, indicator: Any) -> Dict[str, Any]:
        """
        Validate an indicator item.
        
        Args:
            indicator: Indicator data to validate
            
        Returns:
            Validated indicator data
        """
        if not isinstance(indicator, dict):
            return {"type": "unknown", "description": str(indicator)}
        
        validated = indicator.copy()
        
        if "type" not in validated:
            validated["type"] = "unknown"
        elif not isinstance(validated["type"], str):
            validated["type"] = str(validated["type"])
        
        if "description" not in validated:
            validated["description"] = "No description"
        elif not isinstance(validated["description"], str):
            validated["description"] = str(validated["description"])
        
        if "confidence" in validated and not isinstance(validated["confidence"], (int, float)):
            try:
                validated["confidence"] = float(validated["confidence"])
            except (ValueError, TypeError):
                validated["confidence"] = 50
        
        return validated
    
    def _normalize_response(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize response data to ensure consistency.
        
        Args:
            response_data: Response data to normalize
            
        Returns:
            Normalized response data
        """
        normalized = response_data.copy()
        
        # Add metadata
        normalized["validation_timestamp"] = datetime.utcnow().isoformat()
        normalized["validation_version"] = "1.0.0"
        
        # Ensure all required fields have default values if missing (in non-strict mode)
        if not self.enable_strict_validation:
            for field in self.REQUIRED_FIELDS:
                if field not in normalized:
                    normalized[field] = self._get_default_value(field)
        
        return normalized
    
    def _get_default_value(self, field: str) -> Any:
        """
        Get default value for a field.
        
        Args:
            field: Field name
            
        Returns:
            Default value for the field
        """
        defaults = {
            "summary": "No summary provided",
            "observed_indicators": [],
            "possible_interpretation": "No interpretation provided",
            "recommended_investigation_steps": [],
            "confidence_notes": "No confidence notes provided",
            "risk_level": "MEDIUM",
            "urgency": "MEDIUM",
            "investigation_priority": "P2"
        }
        return defaults.get(field, None)
    
    def validate_json_response(self, json_string: str) -> Dict[str, Any]:
        """
        Parse and validate JSON response string.
        
        Args:
            json_string: JSON string to parse and validate
            
        Returns:
            Validated response data
            
        Raises:
            ValueError: If JSON is invalid or response is invalid
        """
        try:
            response_data = json.loads(json_string)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON response: {str(e)}")
        
        return self.validate_analysis_response(response_data)