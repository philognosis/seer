"""
Tests for health check endpoint
"""


def test_health_check(client):
    """Test that health check returns healthy status"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data


def test_api_docs_accessible(client):
    """Test that API docs are accessible"""
    response = client.get("/api/docs")
    assert response.status_code == 200
