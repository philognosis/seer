"""
Tests for voice endpoints
"""


def test_list_voices(client):
    """Test listing available voices"""
    response = client.get("/api/v1/voices/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 4  # At least 4 voices

    # Check voice structure
    voice = data[0]
    assert "id" in voice
    assert "name" in voice
    assert "accent" in voice
    assert "gender" in voice


def test_get_voice(client):
    """Test getting a specific voice"""
    response = client.get("/api/v1/voices/female_us")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "female_us"
    assert data["gender"] == "Female"


def test_get_nonexistent_voice(client):
    """Test getting a voice that doesn't exist"""
    response = client.get("/api/v1/voices/nonexistent")
    assert response.status_code == 404
