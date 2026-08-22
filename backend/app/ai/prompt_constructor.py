from typing import Dict, Any, List, Optional
import logging
import re

logger = logging.getLogger(__name__)


class PromptConstructor:
    """Service for constructing secure prompts for AI analysis."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the prompt constructor.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.max_prompt_length = self.config.get("max_prompt_length", 10000)
        self.enable_input_sanitization = self.config.get("enable_input_sanitization", True)
        self.max_evidence_items = self.config.get("max_evidence_items", 10)
        
    def construct_analysis_prompt(
        self,
        finding_data: Dict[str, Any],
        evidence_data: List[Dict[str, Any]],
        detection_data: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Construct a secure prompt for AI analysis of a finding.
        
        Args:
            finding_data: Finding information
            evidence_data: List of evidence items
            detection_data: Optional detection information
            
        Returns:
            Constructed prompt string
            
        Raises:
            ValueError: If required data is missing or invalid
        """
        logger.info(f"Constructing analysis prompt for finding {finding_data.get('id')}")
        
        # Validate required fields
        if not finding_data.get("title"):
            raise ValueError("Finding title is required")
        
        # Sanitize inputs if enabled
        if self.enable_input_sanitization:
            finding_data = self._sanitize_input(finding_data)
            evidence_data = [self._sanitize_input(evidence) for evidence in evidence_data]
            if detection_data:
                detection_data = self._sanitize_input(detection_data)
        
        # Build prompt sections
        prompt_sections = []
        
        # Add system context
        prompt_sections.append(self._build_system_context())
        
        # Add finding information
        prompt_sections.append(self._build_finding_section(finding_data))
        
        # Add detection information if available
        if detection_data:
            prompt_sections.append(self._build_detection_section(detection_data))
        
        # Add evidence information
        if evidence_data:
            prompt_sections.append(self._build_evidence_section(evidence_data))
        
        # Add analysis instructions
        prompt_sections.append(self._build_analysis_instructions())
        
        # Combine sections
        full_prompt = "\n\n".join(prompt_sections)
        
        # Check prompt length
        if len(full_prompt) > self.max_prompt_length:
            logger.warning(f"Prompt length {len(full_prompt)} exceeds max {self.max_prompt_length}")
            full_prompt = self._truncate_prompt(full_prompt)
        
        logger.info(f"Constructed analysis prompt with {len(full_prompt)} characters")
        return full_prompt
    
    def _build_system_context(self) -> str:
        """Build the system context section of the prompt."""
        return """You are a security analysis AI assistant. Your task is to analyze security findings and provide structured analysis results.

Focus on:
- Identifying the severity and risk level of the finding
- Understanding the context and indicators
- Providing actionable investigation steps
- Maintaining objectivity and avoiding assumptions"""
    
    def _build_finding_section(self, finding_data: Dict[str, Any]) -> str:
        """Build the finding information section of the prompt."""
        section = "## Finding Information\n\n"
        section += f"Title: {finding_data.get('title', 'Unknown')}\n"
        section += f"Description: {finding_data.get('description', 'No description')}\n"
        section += f"Severity: {finding_data.get('severity', 'UNKNOWN')}\n"
        section += f"Confidence: {finding_data.get('confidence', 0)}%\n"
        section += f"Status: {finding_data.get('status', 'UNKNOWN')}\n"
        
        if finding_data.get("created_at"):
            section += f"Created: {finding_data['created_at']}\n"
        
        return section
    
    def _build_detection_section(self, detection_data: Dict[str, Any]) -> str:
        """Build the detection information section of the prompt."""
        section = "## Detection Information\n\n"
        section += f"Detection Rule: {detection_data.get('rule_name', 'Unknown')}\n"
        section += f"Detection Time: {detection_data.get('detected_at', 'Unknown')}\n"
        
        if detection_data.get("description"):
            section += f"Description: {detection_data['description']}\n"
        
        return section
    
    def _build_evidence_section(self, evidence_data: List[Dict[str, Any]]) -> str:
        """Build the evidence information section of the prompt."""
        section = "## Evidence\n\n"
        
        # Limit number of evidence items
        limited_evidence = evidence_data[:self.max_evidence_items]
        
        for i, evidence in enumerate(limited_evidence, 1):
            section += f"### Evidence Item {i}\n"
            section += f"Type: {evidence.get('evidence_type', 'unknown')}\n"
            
            if evidence.get("description"):
                section += f"Description: {evidence['description']}\n"
            
            if evidence.get("source"):
                section += f"Source: {evidence['source']}\n"
            
            if evidence.get("confidence"):
                section += f"Confidence: {evidence['confidence']}%\n"
            
            section += "\n"
        
        if len(evidence_data) > self.max_evidence_items:
            section += f"*Note: Showing {self.max_evidence_items} of {len(evidence_data)} evidence items*\n"
        
        return section
    
    def _build_analysis_instructions(self) -> str:
        """Build the analysis instructions section of the prompt."""
        return """## Analysis Instructions

Please provide a structured analysis with the following components:

1. **Summary**: Brief overview of the finding
2. **Observed Indicators**: List specific indicators from the evidence
3. **Possible Interpretation**: Your assessment of what this finding indicates
4. **Recommended Investigation Steps**: Specific steps for investigating this finding
5. **Confidence Notes**: Comments on the confidence level of your analysis
6. **Risk Level**: Overall risk assessment (HIGH/MEDIUM/LOW)
7. **Urgency**: Recommended urgency level (IMMEDIATE/HIGH/MEDIUM/LOW)
8. **Investigation Priority**: Priority level (P0/P1/P2/P3)

Format your response as structured JSON with these exact field names."""
    
    def _sanitize_input(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitize input data to prevent prompt injection.
        
        Args:
            data: Input data dictionary
            
        Returns:
            Sanitized data dictionary
        """
        sanitized = {}
        
        for key, value in data.items():
            if isinstance(value, str):
                # Remove potential prompt injection patterns
                sanitized_value = self._remove_injection_patterns(value)
                sanitized[key] = sanitized_value
            elif isinstance(value, dict):
                sanitized[key] = self._sanitize_input(value)
            elif isinstance(value, list):
                sanitized[key] = [
                    self._sanitize_input(item) if isinstance(item, dict) else 
                    self._remove_injection_patterns(item) if isinstance(item, str) else item
                    for item in value
                ]
            else:
                sanitized[key] = value
        
        return sanitized
    
    def _remove_injection_patterns(self, text: str) -> str:
        """
        Remove potential prompt injection patterns from text.
        
        Args:
            text: Input text
            
        Returns:
            Sanitized text
        """
        if not isinstance(text, str):
            return text
        
        # Remove common injection patterns
        patterns = [
            r'(?i)ignore\s+(all\s+)?(previous|above)?\s*instructions',
            r'(?i)forget\s+(all\s+)?(previous|above)?\s*instructions',
            r'(?i)disregard\s+(all\s+)?(previous|above)?\s*instructions',
            r'(?i)new\s+instructions?:',
            r'(?i)system\s*:',
            r'(?i)assistant\s*:',
            r'(?i)user\s*:',
            r'(?i)<\|.*?\|>',  # Remove special tokens
            r'(?i)```.*?```',  # Remove code blocks that might contain instructions
        ]
        
        for pattern in patterns:
            text = re.sub(pattern, '[REDACTED]', text)
        
        return text
    
    def _truncate_prompt(self, prompt: str) -> str:
        """
        Truncate prompt to fit within max length.
        
        Args:
            prompt: Full prompt string
            
        Returns:
            Truncated prompt string
        """
        # Truncate from the middle to preserve context
        if len(prompt) <= self.max_prompt_length:
            return prompt
        
        # Keep system context and instructions, truncate evidence section
        parts = prompt.split("## Evidence")
        if len(parts) == 2:
            system_part = parts[0]
            evidence_and_instructions = parts[1]
            
            # Allocate space for system part and instructions
            system_length = len(system_part)
            instructions_length = len("## Analysis Instructions\n\nPlease provide a structured analysis with the following components:\n\n1. **Summary**: Brief overview of the finding\n2. **Observed Indicators**: List specific indicators from the evidence\n3. **Possible Interpretation**: Your assessment of what this finding indicates\n4. **Recommended Investigation Steps**: Specific steps for investigating this finding\n5. **Confidence Notes**: Comments on the confidence level of your analysis\n6. **Risk Level**: Overall risk assessment (HIGH/MEDIUM/LOW)\n7. **Urgency**: Recommended urgency level (IMMEDIATE/HIGH/MEDIUM/LOW)\n8. **Investigation Priority**: Priority level (P0/P1/P2/P3)\n\nFormat your response as structured JSON with these exact field names.")
            
            available_space = self.max_prompt_length - system_length - instructions_length - 100  # Buffer
            
            if available_space > 0:
                truncated_evidence = evidence_and_instructions[:available_space]
                return system_part + "## Evidence" + truncated_evidence + "[...TRUNCATED...]" + "\n\n## Analysis Instructions\n\nPlease provide a structured analysis with the following components:\n\n1. **Summary**: Brief overview of the finding\n2. **Observed Indicators**: List specific indicators from the evidence\n3. **Possible Interpretation**: Your assessment of what this finding indicates\n4. **Recommended Investigation Steps**: Specific steps for investigating this finding\n5. **Confidence Notes**: Comments on the confidence level of your analysis\n6. **Risk Level**: Overall risk assessment (HIGH/MEDIUM/LOW)\n7. **Urgency**: Recommended urgency level (IMMEDIATE/HIGH/MEDIUM/LOW)\n8. **Investigation Priority**: Priority level (P0/P1/P2/P3)\n\nFormat your response as structured JSON with these exact field names."
        
        # Fallback: simple truncation
        return prompt[:self.max_prompt_length - 50] + "\n\n[...PROMPT TRUNCATED...]"