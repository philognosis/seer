"""
Tests for LLM provider endpoints
"""


def test_list_providers(client):
    """Test listing available LLM providers"""
    response = client.get("/api/v1/models/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 3  # gemini, claude, openai

    provider_ids = [p["id"] for p in data]
    assert "gemini" in provider_ids
    assert "claude" in provider_ids
    assert "openai" in provider_ids


def test_get_provider(client):
    """Test getting a specific provider"""
    response = client.get("/api/v1/models/gemini")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "gemini"
    assert "capabilities" in data


def test_get_nonexistent_provider(client):
    """Test getting a provider that doesn't exist"""
    response = client.get("/api/v1/models/nonexistent")
    assert response.status_code == 404
