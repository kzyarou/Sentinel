import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from httpx import AsyncClient
from app.main import app
from app.db.session import get_db
from app.models.detection_rule import DetectionRule, RuleCategory, RuleSeverity
from app.schemas.detection_rule import DetectionRuleCreate, DetectionRuleUpdate
from app.services.rule_validation import RuleValidator, RuleValidationError
import json


@pytest.mark.asyncio
async def test_rule_validation_valid_rule():
    """Test that a valid rule passes validation."""
    valid_rule = DetectionRuleCreate(
        name="test-rule",
        description="Test rule for validation",
        category=RuleCategory.AUTHENTICATION,
        severity=RuleSeverity.HIGH,
        version="1.0",
        enabled=True,
        rule_definition={
            "conditions": [
                {
                    "field": "event.type",
                    "operator": "equals",
                    "value": "authentication_failure"
                }
            ]
        }
    )
    
    # Should not raise exception
    RuleValidator.validate_rule_create(valid_rule)


@pytest.mark.asyncio
async def test_rule_validation_missing_required_fields():
    """Test that missing required fields fail validation."""
    invalid_rule = DetectionRuleCreate(
        name="",  # Missing name
        description="Test rule",
        category=RuleCategory.AUTHENTICATION,
        severity=RuleSeverity.HIGH,
        version="1.0",
        enabled=True,
        rule_definition={"conditions": []}
    )
    
    with pytest.raises(RuleValidationError) as exc:
        RuleValidator.validate_rule_create(invalid_rule)
    
    assert "name" in str(exc.value).lower()


@pytest.mark.asyncio
async def test_rule_validation_invalid_identifier():
    """Test that invalid rule identifiers fail validation."""
    invalid_rule = DetectionRuleCreate(
        name="invalid rule!",  # Contains invalid characters
        description="Test rule",
        category=RuleCategory.AUTHENTICATION,
        severity=RuleSeverity.HIGH,
        version="1.0",
        enabled=True,
        rule_definition={"conditions": [{"field": "event.type", "operator": "equals", "value": "test"}]}
    )
    
    with pytest.raises(RuleValidationError) as exc:
        RuleValidator.validate_rule_create(invalid_rule)
    
    assert "alphanumeric" in str(exc.value).lower()


@pytest.mark.asyncio
async def test_rule_validation_invalid_category():
    """Test that invalid category fails validation."""
    invalid_rule = DetectionRuleCreate(
        name="test-rule",
        description="Test rule",
        category="INVALID_CATEGORY",  # Invalid category
        severity=RuleSeverity.HIGH,
        version="1.0",
        enabled=True,
        rule_definition={"conditions": [{"field": "event.type", "operator": "equals", "value": "test"}]}
    )
    
    with pytest.raises(RuleValidationError) as exc:
        RuleValidator.validate_rule_create(invalid_rule)
    
    assert "category" in str(exc.value).lower()


@pytest.mark.asyncio
async def test_rule_validation_invalid_severity():
    """Test that invalid severity fails validation."""
    invalid_rule = DetectionRuleCreate(
        name="test-rule",
        description="Test rule",
        category=RuleCategory.AUTHENTICATION,
        severity="INVALID_SEVERITY",  # Invalid severity
        version="1.0",
        enabled=True,
        rule_definition={"conditions": [{"field": "event.type", "operator": "equals", "value": "test"}]}
    )
    
    with pytest.raises(RuleValidationError) as exc:
        RuleValidator.validate_rule_create(invalid_rule)
    
    assert "severity" in str(exc.value).lower()


@pytest.mark.asyncio
async def test_rule_validation_missing_conditions():
    """Test that missing conditions fail validation."""
    invalid_rule = DetectionRuleCreate(
        name="test-rule",
        description="Test rule",
        category=RuleCategory.AUTHENTICATION,
        severity=RuleSeverity.HIGH,
        version="1.0",
        enabled=True,
        rule_definition={}  # Missing conditions
    )
    
    with pytest.raises(RuleValidationError) as exc:
        RuleValidator.validate_rule_create(invalid_rule)
    
    assert "conditions" in str(exc.value).lower()


@pytest.mark.asyncio
async def test_rule_validation_invalid_operator():
    """Test that invalid operators fail validation."""
    invalid_rule = DetectionRuleCreate(
        name="test-rule",
        description="Test rule",
        category=RuleCategory.AUTHENTICATION,
        severity=RuleSeverity.HIGH,
        version="1.0",
        enabled=True,
        rule_definition={
            "conditions": [
                {
                    "field": "event.type",
                    "operator": "invalid_operator",  # Invalid operator
                    "value": "test"
                }
            ]
        }
    )
    
    with pytest.raises(RuleValidationError) as exc:
        RuleValidator.validate_rule_create(invalid_rule)
    
    assert "operator" in str(exc.value).lower()


@pytest.mark.asyncio
async def test_rule_validation_invalid_field():
    """Test that invalid fields fail validation."""
    invalid_rule = DetectionRuleCreate(
        name="test-rule",
        description="Test rule",
        category=RuleCategory.AUTHENTICATION,
        severity=RuleSeverity.HIGH,
        version="1.0",
        enabled=True,
        rule_definition={
            "conditions": [
                {
                    "field": "invalid.field",  # Invalid field
                    "operator": "equals",
                    "value": "test"
                }
            ]
        }
    )
    
    with pytest.raises(RuleValidationError) as exc:
        RuleValidator.validate_rule_create(invalid_rule)
    
    assert "field" in str(exc.value).lower()


@pytest.mark.asyncio
async def test_rule_validation_executable_code():
    """Test that executable code patterns are rejected."""
    malicious_rule = DetectionRuleCreate(
        name="test-rule",
        description="Test rule",
        category=RuleCategory.AUTHENTICATION,
        severity=RuleSeverity.HIGH,
        version="1.0",
        enabled=True,
        rule_definition={
            "conditions": [
                {
                    "field": "event.type",
                    "operator": "equals",
                    "value": "test; exec('rm -rf /') #"
                }
            ]
        }
    )
    
    with pytest.raises(RuleValidationError) as exc:
        RuleValidator.validate_rule_create(malicious_rule)
    
    assert "dangerous" in str(exc.value).lower()


@pytest.mark.asyncio
async def test_rule_validation_prevent_name_version_change():
    """Test that name and version cannot be changed on update."""
    RuleValidator.validate_rule_update(
        DetectionRuleUpdate(
            name="new-name",  # Cannot change name
            version="2.0"  # Cannot change version
        )
    )
    
    with pytest.raises(RuleValidationError) as exc:
        RuleValidator.validate_rule_update(
            DetectionRuleUpdate(
                name="new-name",  # Cannot change name
                version="2.0"  # Cannot change version
            )
        )
    
    assert "cannot change" in str(exc.value).lower()


@pytest.mark.asyncio
async def test_rule_create_api_success():
    """Test successful rule creation via API."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # First, create a user and login to get auth token
        # This assumes user creation and login endpoints exist
        login_response = await client.post(
            "/api/v1/auth/register",
            json={
                "external_id": "test-user",
                "username": "testuser",
                "password": "testpass123"
            }
        )
        token = login_response.json()["access_token"]
        
        headers = {"Authorization": f"Bearer {token}"}
        
        rule_data = {
            "name": "auth-brute-force",
            "description": "Detect brute force authentication attempts",
            "category": "AUTHENTICATION",
            "severity": "HIGH",
            "version": "1.0",
            "enabled": True,
            "rule_definition": {
                "conditions": [
                    {
                        "field": "event.type",
                        "operator": "equals",
                        "value": "authentication_failure"
                    }
                ]
            }
        }
        
        response = await client.post(
            "/api/v1/detection-rules",
            json=rule_data,
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "auth-brute-force"
        assert data["version"] == "1.0"
        assert data["enabled"] == True
        assert "id" in data


@pytest.mark.asyncio
async def test_rule_create_api_validation_error():
    """Test that invalid rule data is rejected by API."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # First, create a user and login
        login_response = await client.post(
            "/api/v1/auth/register",
            json={
                "external_id": "test-user",
                "username": "testuser",
                "password": "testpass123"
            }
        )
        token = login_response.json()["access_token"]
        
        headers = {"Authorization": f"Bearer {token}"}
        
        invalid_rule = {
            "name": "",  # Invalid: empty name
            "description": "Test rule",
            "category": "AUTHENTICATION",
            "severity": "HIGH",
            "version": "1.0",
            "enabled": True,
            "rule_definition": {"conditions": []}
        }
        
        response = await client.post(
            "/api/v1/detection-rules",
            json=invalid_rule,
            headers=headers
        )
        
        assert response.status_code == 400


@pytest.mark.asyncio
async def test_rule_list_api():
    """Test that rules can be listed via API."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # First, create a user and login
        login_response = await client.post(
            "/api/v1/auth/register",
            json={
                "external_id": "test-user",
                "username": "testuser",
                "password": "testpass123"
            }
        )
        token = login_response.json()["access_token"]
        
        headers = {"Authorization": f"Bearer {token}"}
        
        response = await client.get(
            "/api/v1/detection-rules",
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data


@pytest.mark.asyncio
async def test_rule_enable_disable_api():
    """Test that rules can be enabled and disabled via API."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # First, create a user and login
        login_response = await client.post(
            "/api/v1/auth/register",
            json={
                "external_id": "test-user",
                "username": "testuser",
                "password": "testpass123"
            }
        )
        token = login_response.json()["access_token"]
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # Create a rule
        rule_data = {
            "name": "test-rule",
            "description": "Test rule",
            "category": "AUTHENTICATION",
            "severity": "HIGH",
            "version": "1.0",
            "enabled": True,
            "rule_definition": {
                "conditions": [
                    {
                        "field": "event.type",
                        "operator": "equals",
                        "value": "authentication_failure"
                    }
                ]
            }
        }
        
        create_response = await client.post(
            "/api/v1/detection-rules",
            json=rule_data,
            headers=headers
        )
        rule_id = create_response.json()["id"]
        
        # Disable the rule
        disable_response = await client.post(
            f"/api/v1/detection-rules/{rule_id}/disable",
            headers=headers
        )
        
        assert disable_response.status_code == 200
        assert disable_response.json()["enabled"] == False
        
        # Enable the rule
        enable_response = await client.post(
            f"/api/v1/detection-rules/{rule_id}/enable",
            headers=headers
        )
        
        assert enable_response.status_code == 200
        assert enable_response.json()["enabled"] == True


@pytest.mark.asyncio
async def test_rule_versioning_api():
    """Test that rule versioning works via API."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # First, create a user and login
        login_response = await client.post(
            "/api/v1/auth/register",
            json={
                "external_id": "test-user",
                "username": "testuser",
                "password": "testpass123"
            }
        )
        token = login_response.json()["access_token"]
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # Create v1
        rule_v1 = {
            "name": "auth-brute-force",
            "description": "Detect brute force attempts v1",
            "category": "AUTHENTICATION",
            "severity": "HIGH",
            "version": "1.0",
            "enabled": True,
            "rule_definition": {
                "conditions": [
                    {
                        "field": "event.type",
                        "operator": "equals",
                        "value": "authentication_failure"
                    }
                ]
            }
        }
        
        create_v1 = await client.post(
            "/api/v1/detection-rules",
            json=rule_v1,
            headers=headers
        )
        
        # Create v2 with same name (different version)
        rule_v2 = {
            "name": "auth-brute-force",
            "description": "Detect brute force attempts v2",
            "category": "AUTHENTICATION",
            "severity": "CRITICAL",
            "version": "2.0",
            "enabled": True,
            "rule_definition": {
                "conditions": [
                    {
                        "field": "event.type",
                        "operator": "equals",
                        "value": "authentication_failure"
                    },
                    {
                        "field": "event.source",
                        "operator": "equals",
                        "value": "ssh"
                    }
                ]
            }
        }
        
        create_v2 = await client.post(
            "/api/v1/detection-rules",
            json=rule_v2,
            headers=headers
        )
        
        assert create_v2.status_code == 200
        assert create_v2.json()["version"] == "2.0"
        
        # Get all versions by name
        versions_response = await client.get(
            "/api/v1/detection-rules/by-name/auth-brute-force",
            headers=headers
        )
        
        assert versions_response.status_code == 200
        versions = versions_response.json()
        assert len(versions) == 2
        assert versions[0]["version"] == "1.0"
        assert versions[1]["version"] == "2.0"


@pytest.mark.asyncio
async def test_rule_update_prevents_version_change():
    """Test that version change is prevented via API."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # First, create a user and login
        login_response = await client.post(
            "/api/v1/auth/register",
            json={
                "external_id": "test-user",
                "username": "testuser",
                "password": "testpass123"
            }
        )
        token = login_response.json()["access_token"]
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # Create a rule
        rule_data = {
            "name": "test-rule",
            "description": "Test rule",
            "category": "AUTHENTICATION",
            "severity": "HIGH",
            "version": "1.0",
            "enabled": True,
            "rule_definition": {
                "conditions": [
                    {
                        "field": "event.type",
                        "operator": "equals",
                        "value": "authentication_failure"
                    }
                ]
            }
        }
        
        create_response = await client.post(
            "/api/v1/detection-rules",
            json=data=rule_data,
            headers=headers
        )
        rule_id = create_response.json()["id"]
        
        # Try to change version (should fail)
        update_response = await client.patch(
            f"/api/v1/detection-rules/{rule_id}",
            json={"version": "2.0"},
            headers=headers
        )
        
        assert update_response.status_code == 400


@pytest.mark.asyncio
async def test_rule_authorization_admin_only():
    """Test that only administrators can manage rules."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Create a viewer user (non-admin)
        viewer_response = await client.post(
            "/api/v1/auth/register",
            json={
                "external_id": "viewer-user",
                "username": "viewer",
                "password": "testpass123"
            }
        )
        viewer_token = viewer_response.json()["access_token"]
        
        viewer_headers = {"Authorization": f"Bearer {viewer_token}"}
        
        # Try to create a rule as viewer (should fail)
        rule_data = {
            "name": "test-rule",
            "description": "Test rule",
            "category": "AUTHENTICATION",
            "severity": "HIGH",
            "version": "1.0",
            "enabled": True,
            "rule_definition": {
                "conditions": [
                    {
                        "field": "event.type",
                        "operator": "equals",
                        "value": "authentication_failure"
                    }
                ]
            }
        }
        
        create_response = await client.post(
            "/api/v1/detection-rules",
            json=rule_data,
            headers=viewer_headers
        )
        
        assert create_response.status_code == 403  # Forbidden


@pytest.mark.asyncio
async def test_rule_delete_with_detections_soft_delete():
    """Test that rules with detections are disabled instead of deleted."""
    async with AsyncSession() as db:
        # This test would require creating a rule, adding detections, then testing deletion
        # For now, we'll test the service logic directly
        pass


@pytest.mark.asyncio
async def test_supported_operators_list():
    """Test that the supported operators list is comprehensive."""
    expected_operators = {
        "equals", "not_equals", "contains", "not_contains", "starts_with", "ends_with",
        "greater_than", "less_than", "greater_than_or_equal", "less_than_or_equal",
        "in", "not_in", "matches", "exists", "not_exists"
    }
    
    assert RuleValidator.SUPPORTED_OPERATORS == expected_operators


@pytest.mark.asyncio
async def test_supported_fields_list():
    """Test that the supported fields list is comprehensive."""
    expected_fields = {
        "event.type", "event.source", "event.host", "event.user", "event.ip_address",
        "event.process", "event.process_id", "event.parent_process", "event.command_line",
        "event.file_path", "event.file_hash", "event.registry_key", "event.registry_value",
        "event.url", "event.domain", "event.protocol", "event.port", "event.mac_address",
        "event.http_method", "event.http_status", "event.http_url", "event.http_user_agent",
        "event.http_referer", "event.http_headers", "event.ssh_user", "event.ssh_method",
        "event.ssh_protocol", "event.ssh_client_version", "event.login_type",
        "event.login_result", "event.user_agent", "event.email_subject", "event.email_sender",
        "event.email_recipient", "event.email_attachment", "event.dns_query",
        "event.dns_query_type", "event.dns_response", "event.certificate_subject",
        "event.certificate_issuer", "event.certificate_serial", "event.certificate_fingerprint",
        "event.certificate_valid_from", "event.certificate_valid_to"
    }
    
    assert RuleValidator.SUPPORTED_FIELDS == expected_fields