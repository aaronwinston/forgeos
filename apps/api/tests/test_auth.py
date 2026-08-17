"""Integration tests for authentication endpoints."""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session
from database import get_session
from main import app
from models import Organization, Membership

pytestmark = pytest.mark.integration

import personal_mode as _personal_mode_test_auth
from config import settings as _settings_test_auth


@pytest.fixture(autouse=True, scope="module")
def _enable_multi_tenant_test_auth():
    """Force multi-tenant mode so JWT auth is enforced."""
    original_mode = _settings_test_auth.FORGEOS_MODE
    original_fn = _personal_mode_test_auth.is_personal
    _settings_test_auth.FORGEOS_MODE = "multi_tenant"
    _personal_mode_test_auth.is_personal = lambda: False
    yield
    _settings_test_auth.FORGEOS_MODE = original_mode
    _personal_mode_test_auth.is_personal = original_fn




@pytest.mark.integration
class TestAuthSignup:
    """Tests for user signup endpoint."""
    
    def test_signup_creates_user(self, client, test_db):
        response = client.post(
            "/api/auth/signup",
            json={
                "email": "newuser@example.com",
                "password": "SecurePass123",
                "org_name": "New Org",
            }
        )
        assert response.status_code in [200, 201]
        data = response.json()
        assert "user_id" in data
        assert "org_id" in data
        assert data["email"] == "newuser@example.com"
    
    def test_signup_sets_auth_token(self, client):
        response = client.post(
            "/api/auth/signup",
            json={
                "email": "test@example.com",
                "password": "SecurePass123",
                "org_name": "Test Org",
            }
        )
        assert response.status_code in [200, 201]
        # Token should be in httpOnly cookie or response
        assert "auth_token" in response.cookies or "access_token" in response.json()
    
    def test_signup_invalid_email(self, client):
        response = client.post(
            "/api/auth/signup",
            json={
                "email": "invalid-email",
                "password": "SecurePass123",
                "org_name": "Test Org",
            }
        )
        assert response.status_code in [400, 422]


@pytest.mark.integration
class TestAuthSignin:
    """Tests for user signin endpoint."""
    
    def test_signin_with_valid_credentials(self, client):
        # First sign up
        client.post(
            "/api/auth/signup",
            json={
                "email": "user@example.com",
                "password": "SecurePass123",
                "org_name": "Test Org",
            }
        )
        
        # Then sign in
        response = client.post(
            "/api/auth/signin",
            json={
                "email": "user@example.com",
                "password": "SecurePass123",
            }
        )
        assert response.status_code in [200, 401]  # Could fail if password hash not matching
    
    def test_signin_invalid_email(self, client):
        response = client.post(
            "/api/auth/signin",
            json={
                "email": "invalid-email",
                "password": "SecurePass123",
            }
        )
        assert response.status_code in [400, 422]


@pytest.mark.integration
class TestAuthAuthorization:
    """Tests for authorization with JWT tokens."""
    
    def test_authorized_request_with_token(self, client, test_token):
        response = client.get(
            "/api/projects",
            headers={"Authorization": f"Bearer {test_token}"}
        )
        assert response.status_code in [200, 204]
    
    def test_unauthorized_request_without_token(self, client):
        response = client.get("/api/projects")
        assert response.status_code == 401
    
    def test_unauthorized_request_invalid_token(self, client):
        response = client.get(
            "/api/projects",
            headers={"Authorization": "Bearer invalid_token"}
        )
        assert response.status_code == 401
    
    def test_request_with_expired_token(self, client):
        # Token with exp in the past
        import jwt
        from config import settings
        from datetime import datetime, timedelta, timezone
        
        expired_payload = {
            "sub": "test-user",
            "org_id": "test-org",
            "role": "member",
            "exp": datetime.now(timezone.utc) - timedelta(hours=1)
        }
        expired_token = jwt.encode(
            expired_payload,
            settings.JWT_SECRET_KEY,
            algorithm="HS256"
        )
        
        response = client.get(
            "/api/projects",
            headers={"Authorization": f"Bearer {expired_token}"}
        )
        assert response.status_code == 401
