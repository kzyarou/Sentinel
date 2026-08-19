import pytest
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_check():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_readiness_check_endpoint_exists():
    """Test that readiness endpoint exists and returns expected structure."""
    # This test will fail if DB is not available, which is expected
    response = client.get("/api/v1/health/ready")
    # Either returns 200 with connected status or 503 if DB unavailable
    assert response.status_code in [200, 503]
    if response.status_code == 200:
        assert response.json() == {
            "status": "ready",
            "database": "connected"
        }
    else:
        assert "database connection failed" in response.json()["detail"]
