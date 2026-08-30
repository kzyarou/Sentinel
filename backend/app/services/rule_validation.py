from typing import Dict, Any, List, Optional
from app.schemas.detection_rule import DetectionRuleCreate, DetectionRuleUpdate


class RuleValidationError(Exception):
    """Raised when rule validation fails."""
    def __init__(self, message: str, field: Optional[str] = None):
        self.message = message
        self.field = field
        super().__init__(self.message)


class RuleValidator:
    """Validates detection rules before they become active."""
    
    # Supported operators for rule conditions
    SUPPORTED_OPERATORS = {
        "equals",
        "not_equals",
        "contains",
        "not_contains",
        "starts_with",
        "ends_with",
        "greater_than",
        "less_than",
        "greater_than_or_equal",
        "less_than_or_equal",
        "in",
        "not_in",
        "matches",
        "exists",
        "not_exists"
    }
    
    # Supported fields for rule conditions
    SUPPORTED_FIELDS = {
        "event.type",
        "event.source",
        "event.host",
        "event.user",
        "event.ip_address",
        "event.process",
        "event.process_id",
        "event.parent_process",
        "event.command_line",
        "event.file_path",
        "event.file_hash",
        "event.registry_key",
        "event.registry_value",
        "event.url",
        "event.domain",
        "event.protocol",
        "event.port",
        "event.mac_address",
        "event.http_method",
        "event.http_status",
        "event.http_url",
        "event.http_user_agent",
        "event.http_referer",
        "event.http_headers",
        "event.ssh_user",
        "event.ssh_method",
        "event.ssh_protocol",
        "event.ssh_client_version",
        "event.login_type",
        "event.login_result",
        "event.user_agent",
        "event.email_subject",
        "event.email_sender",
        "event.email_recipient",
        "event.email_attachment",
        "event.dns_query",
        "event.dns_query_type",
        "event.dns_response",
        "event.certificate_subject",
        "event.certificate_issuer",
        "event.certificate_serial",
        "event.certificate_fingerprint",
        "event.certificate_valid_from",
        "event.certificate_valid_to",
    }
    
    @classmethod
    def validate_rule_create(cls, rule_data: DetectionRuleCreate) -> None:
        """Validate a new detection rule before creation."""
        cls._validate_required_fields(rule_data)
        cls._validate_identifier(rule_data.name, rule_data.version)
        cls._validate_severity(rule_data.severity)
        cls._validate_category(rule_data.category)
        cls._validate_rule_definition(rule_data.rule_definition)
        cls._validate_no_executable_code(rule_data.rule_definition)
    
    @classmethod
    def validate_rule_update(cls, rule_data: DetectionRuleUpdate) -> None:
        """Validate detection rule update."""
        if rule_data.name is not None or rule_data.version is not None:
            raise RuleValidationError(
                "Cannot change rule name or version. Create a new version instead.",
                field="name"
            )
        
        if rule_data.category is not None:
            cls._validate_category(rule_data.category)
        
        if rule_data.severity is not None:
            cls._validate_severity(rule_data.severity)
        
        if rule_data.rule_definition is not None:
            cls._validate_rule_definition(rule_data.rule_definition)
            cls._validate_no_executable_code(rule_data.rule_definition)
    
    @classmethod
    def _validate_required_fields(cls, rule_data: DetectionRuleCreate) -> None:
        """Validate that all required fields are present."""
        if not rule_data.name or not rule_data.name.strip():
            raise RuleValidationError("Rule name is required", field="name")
        
        if not rule_data.version or not rule_data.version.strip():
            raise RuleValidationError("Rule version is required", field="version")
        
        if not rule_data.category:
            raise RuleValidationError("Rule category is required", field="category")
        
        if not rule_data.severity:
            raise RuleValidationError("Rule severity is required", field="severity")
        
        if not rule_data.rule_definition:
            raise RuleValidationError("Rule definition is required", field="rule_definition")
    
    @classmethod
    def _validate_identifier(cls, name: str, version: str) -> None:
        """Validate rule identifier format."""
        if not name or len(name) > 255:
            raise RuleValidationError("Rule name must be 1-255 characters", field="name")
        
        if not version or len(version) > 50:
            raise RuleValidationError("Rule version must be 1-50 characters", field="version")
        
        # Check for valid characters in name (alphanumeric, hyphens, underscores)
        if not all(c.isalnum() or c in ('-', '_') for c in name):
            raise RuleValidationError(
                "Rule name can only contain alphanumeric characters, hyphens, and underscores",
                field="name"
            )
    
    @classmethod
    def _validate_severity(cls, severity: str) -> None:
        """Validate rule severity."""
        valid_severities = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
        if severity not in valid_severities:
            raise RuleValidationError(
                f"Invalid severity. Must be one of: {', '.join(valid_severities)}",
                field="severity"
            )
    
    @classmethod
    def _validate_category(cls, category: str) -> None:
        """Validate rule category."""
        valid_categories = [
            "AUTHENTICATION", "ACCESS_CONTROL", "NETWORK", "PROCESS", 
            "ENDPOINT", "SYSTEM", "OTHER"
        ]
        if category not in valid_categories:
            raise RuleValidationError(
                f"Invalid category. Must be one of: {', '.join(valid_categories)}",
                field="category"
            )
    
    @classmethod
    def _validate_rule_definition(cls, rule_definition: Dict[str, Any]) -> None:
        """Validate rule definition structure."""
        if not isinstance(rule_definition, dict):
            raise RuleValidationError("Rule definition must be a dictionary", field="rule_definition")
        
        # Check for required structure
        if "conditions" not in rule_definition:
            raise RuleValidationError("Rule definition must contain 'conditions' field", field="rule_definition")
        
        conditions = rule_definition["conditions"]
        if not isinstance(conditions, list):
            raise RuleValidationError("Rule conditions must be a list", field="rule_definition.conditions")
        
        if not conditions:
            raise RuleValidationError("Rule must have at least one condition", field="rule_definition.conditions")
        
        # Validate each condition
        for i, condition in enumerate(conditions):
            cls._validate_condition(condition, i)
    
    @classmethod
    def _validate_condition(cls, condition: Dict[str, Any], index: int) -> None:
        """Validate a single rule condition."""
        if not isinstance(condition, dict):
            raise RuleValidationError(
                f"Condition {index} must be a dictionary",
                field=f"rule_definition.conditions[{index}]"
            )
        
        required_fields = ["field", "operator", "value"]
        for field in required_fields:
            if field not in condition:
                raise RuleValidationError(
                    f"Condition {index} missing required field: {field}",
                    field=f"rule_definition.conditions[{index}].{field}"
                )
        
        # Validate field
        field = condition["field"]
        if field not in cls.SUPPORTED_FIELDS:
            raise RuleValidationError(
                f"Condition {index} has unsupported field: {field}. Supported fields: {', '.join(sorted(cls.SUPPORTED_FIELDS))}",
                field=f"rule_definition.conditions[{index}].field"
            )
        
        # Validate operator
        operator = condition["operator"]
        if operator not in cls.SUPPORTED_OPERATORS:
            raise RuleValidationError(
                f"Condition {index} has unsupported operator: {operator}. Supported operators: {', '.join(sorted(cls.SUPPORTED_OPERATORS))}",
                field=f"rule_definition.conditions[{index}].operator"
            )
        
        # Validate value based on operator
        cls._validate_condition_value(condition["value"], operator, index)
    
    @classmethod
    def _validate_condition_value(cls, value: Any, operator: str, index: int) -> None:
        """Validate condition value based on operator."""
        list_operators = {"in", "not_in"}
        string_operators = {"contains", "not_contains", "starts_with", "ends_with", "matches"}
        numeric_operators = {"greater_than", "less_than", "greater_than_or_equal", "less_than_or_equal"}
        
        if operator in list_operators:
            if not isinstance(value, list):
                raise RuleValidationError(
                    f"Condition {index} value must be a list for operator '{operator}'",
                    field=f"rule_definition.conditions[{index}].value"
                )
        elif operator in string_operators:
            if not isinstance(value, str):
                raise RuleValidationError(
                    f"Condition {index} value must be a string for operator '{operator}'",
                    field=f"rule_definition.conditions[{index}].value"
                )
        elif operator in numeric_operators:
            if not isinstance(value, (int, float)):
                raise RuleValidationError(
                    f"Condition {index} value must be numeric for operator '{operator}'",
                    field=f"rule_definition.conditions[{index}].value"
                )
    
    @classmethod
    def _validate_no_executable_code(cls, rule_definition: Dict[str, Any]) -> None:
        """Ensure rule definition contains no executable code."""
        dangerous_patterns = [
            "eval(",
            "exec(",
            "execfile(",
            "compile(",
            "__import__",
            "open(",
            "file(",
            "input(",
            "globals(",
            "locals(",
            "vars(",
            "getattr(",
            "setattr(",
            "delattr(",
            "hasattr(",
            "callable(",
            "import ",
            "from ",
            "class ",
            "def ",
            "lambda ",
            ";",
            "$(",
            "`",
            "${",
            "{{",
            "{%",
        ]
        
        rule_str = str(rule_definition).lower()
        
        for pattern in dangerous_patterns:
            if pattern in rule_str:
                raise RuleValidationError(
                    f"Rule definition contains potentially dangerous pattern: {pattern}",
                    field="rule_definition"
                )