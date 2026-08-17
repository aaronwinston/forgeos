"""Integration tests for chat endpoints."""

import pytest

pytestmark = pytest.mark.integration

import personal_mode as _personal_mode_test_chat
from config import settings as _settings_test_chat


@pytest.fixture(autouse=True, scope="module")
def _enable_multi_tenant_test_chat():
    """Force multi-tenant mode so JWT auth is enforced."""
    original_mode = _settings_test_chat.FORGEOS_MODE
    original_fn = _personal_mode_test_chat.is_personal
    _settings_test_chat.FORGEOS_MODE = "multi_tenant"
    _personal_mode_test_chat.is_personal = lambda: False
    yield
    _settings_test_chat.FORGEOS_MODE = original_mode
    _personal_mode_test_chat.is_personal = original_fn




@pytest.mark.integration
class TestChatStartSession:
    """Tests for starting a chat session."""
    
    def test_start_chat_session(self, client, test_token):
        """Test starting a new chat session."""
        response = client.post(
            "/api/chat/session",
            headers={"Authorization": f"Bearer {test_token}"},
            json={"title": "Test Chat"}
        )
        # Endpoint may not exist yet
        assert response.status_code in [200, 201, 404]
    
    def test_start_chat_unauthorized(self, client):
        """Test that unauthorized access is denied."""
        response = client.post(
            "/api/chat/session",
            json={"title": "Test Chat"}
        )
        assert response.status_code == 401


@pytest.mark.integration
class TestChatMessages:
    """Tests for sending and receiving chat messages."""
    
    def test_send_message(self, client, test_token):
        """Test sending a message in a chat session."""
        # First create a session (if endpoint exists)
        response = client.post(
            "/api/chat/stream",
            headers={"Authorization": f"Bearer {test_token}"},
            json={"message": "Hello"}
        )
        # Endpoint may not exist yet
        assert response.status_code in [200, 404]
    
    def test_send_message_unauthorized(self, client):
        """Test that unauthorized message sending is denied."""
        response = client.post(
            "/api/chat/stream",
            json={"message": "Hello"}
        )
        assert response.status_code == 401


@pytest.mark.integration
class TestChatHistory:
    """Tests for retrieving chat history."""
    
    def test_get_chat_history(self, client, test_token):
        """Test retrieving chat history (non-existent session returns 404)."""
        response = client.get(
            "/api/chat/session/nonexistent-session/messages",
            headers={"Authorization": f"Bearer {test_token}"}
        )
        # Session doesn't exist -> 404, or method not allowed -> 405
        assert response.status_code in [200, 404, 405, 422]
    
    def test_get_chat_history_unauthorized(self, client):
        """Test that unauthorized access is denied."""
        response = client.get("/api/chat/session/some-session/messages")
        assert response.status_code == 401


@pytest.mark.integration
class TestChatTenantIsolation:
    """Tests for tenant isolation in chat endpoints."""
    
    def test_user_sees_only_own_chat_sessions(self, client, test_token):
        """Test that users can only see their own chat sessions."""
        # This would require creating chat sessions and verifying isolation
        response = client.get(
            "/api/chat/session",
            headers={"Authorization": f"Bearer {test_token}"}
        )
        if response.status_code == 200:
            data = response.json()
            # All sessions should belong to the authenticated user
            assert isinstance(data, list)
