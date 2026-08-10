import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from app.main import app

client = TestClient(app)

from app.api.routes.voice import get_stt_provider, get_tts_provider

@pytest.fixture
def mock_groq_provider():
    provider = Mock()
    from app.voice.stt.provider import TranscriptResponse
    provider.transcribe.return_value = TranscriptResponse(
        text="Show me order OR 603",
        provider="MockGroq",
        model="whisper-large-v3-turbo"
    )
    app.dependency_overrides[get_stt_provider] = lambda: provider
    yield provider
    app.dependency_overrides.pop(get_stt_provider, None)

@pytest.fixture
def mock_tts_provider():
    provider = Mock()
    provider.synthesize.return_value = b"mock audio data"
    app.dependency_overrides[get_tts_provider] = lambda: provider
    yield provider
    app.dependency_overrides.pop(get_tts_provider, None)

def test_transcribe_audio_endpoint(mock_groq_provider):
    # Create a dummy audio file
    files = {"file": ("test.webm", b"dummy audio content", "audio/webm")}
    
    response = client.post("/api/voice/transcribe", files=files)
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "success"
    # Normalizer should have converted "OR 603" to "OR603"
    assert data["transcript"] == "Show me order OR603"
    assert data["provider"] == "MockGroq"

def test_transcribe_invalid_audio_type():
    files = {"file": ("test.txt", b"dummy text content", "text/plain")}
    response = client.post("/api/voice/transcribe", files=files)
    assert response.status_code == 400
    assert "Unsupported file type" in response.json()["detail"]

def test_transcribe_empty_audio():
    files = {"file": ("test.webm", b"", "audio/webm")}
    response = client.post("/api/voice/transcribe", files=files)
    assert response.status_code == 400
    assert "Empty audio file" in response.json()["detail"]

def test_tts_endpoint(mock_tts_provider):
    response = client.post("/api/voice/tts", json={"text": "Hello world"})
    assert response.status_code == 200
    assert response.content == b"mock audio data"
    assert response.headers["content-type"] == "audio/mpeg"
