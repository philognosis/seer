"""
Tests for video endpoints
"""
import io


def test_get_video_status(client):
    """Test getting video processing status"""
    response = client.get("/api/v1/videos/test-id/status")
    assert response.status_code == 200
    data = response.json()
    assert data["video_id"] == "test-id"
    assert "status" in data
    assert "progress" in data


def test_upload_invalid_file_type(client):
    """Test uploading an invalid file type"""
    file_content = b"not a video"
    response = client.post(
        "/api/v1/videos/upload",
        files={"file": ("test.txt", io.BytesIO(file_content), "text/plain")},
        data={"voice": "female_us", "llm_provider": "gemini", "description_density": "standard"},
    )
    assert response.status_code == 422


def test_process_from_invalid_url(client):
    """Test processing from an invalid URL"""
    response = client.post(
        "/api/v1/videos/from-url",
        json={
            "url": "https://not-a-supported-site.com/video",
            "options": {"voice": "female_us"},
        },
    )
    assert response.status_code == 422


def test_delete_nonexistent_video(client):
    """Test deleting a video that doesn't exist"""
    response = client.delete("/api/v1/videos/nonexistent-id")
    # Should succeed silently (idempotent)
    assert response.status_code == 200
