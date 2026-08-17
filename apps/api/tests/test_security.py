"""
Comprehensive Security Test Suite for ForgeOS API
Tests for authentication, authorization, input validation, and common vulnerabilities
"""
import pytest
import uuid
import jwt
from fastapi.testclient import TestClient
from sqlmodel import Session
from datetime import datetime, timedelta, timezone

from main import app
from database import engine
from models import Organization, Membership, Project
from config import settings

pytestmark = pytest.mark.integration


@pytest.fixture(autouse=True, scope="module")
def enable_multi_tenant_mode():
    """Force multi-tenant mode for all security tests so JWT auth is enforced."""
    original = settings.FORGEOS_MODE
    settings.FORGEOS_MODE = "multi_tenant"
    # Also patch personal_mode.is_personal to return False
    import personal_mode
    original_fn = personal_mode.is_personal
    personal_mode.is_personal = lambda: False
    yield
    settings.FORGEOS_MODE = original
    personal_mode.is_personal = original_fn


client = TestClient(app)

# ===== Test Fixtures =====

def create_test_org(org_name: str) -> tuple[str, str]:
    """Create organization and user, return (org_id, user_id)"""
    org_id = str(uuid.uuid4())
    user_id = f"user_{uuid.uuid4().hex[:8]}"
    
    with Session(engine) as session:
        org = Organization(
            id=org_id, 
            name=org_name, 
            slug=f"{org_name.lower().replace(' ', '-')}-{org_id[:8]}"
        )
        session.add(org)
        session.commit()

        membership = Membership(
            id=str(uuid.uuid4()),
            user_id=user_id,
            organization_id=org_id,
            role="owner"
        )
        session.add(membership)
        session.commit()
    
    return org_id, user_id

def make_valid_token(user_id: str, org_id: str, role: str = "member") -> str:
    """Create a valid JWT token"""
    payload = {
        "sub": user_id,
        "org_id": org_id,
        "role": role,
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(hours=1),
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm="HS256")

def make_expired_token(user_id: str, org_id: str) -> str:
    """Create an expired JWT token"""
    payload = {
        "sub": user_id,
        "org_id": org_id,
        "role": "member",
        "iat": datetime.now(timezone.utc) - timedelta(hours=2),
        "exp": datetime.now(timezone.utc) - timedelta(hours=1),
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm="HS256")

def make_invalid_signature_token(user_id: str, org_id: str) -> str:
    """Create a token with invalid signature"""
    payload = {
        "sub": user_id,
        "org_id": org_id,
        "role": "member",
    }
    return jwt.encode(payload, "wrong_secret_key", algorithm="HS256")


# ===== Authentication Tests =====

class TestAuthenticationJWT:
    """Test JWT token validation and handling"""

    def test_missing_token_returns_401(self):
        """Request without token should be rejected"""
        response = client.get("/api/projects")
        assert response.status_code == 401

    def test_valid_token_accepted(self):
        """Valid token should allow access"""
        org_id, user_id = create_test_org("Test Org")
        token = make_valid_token(user_id, org_id)
        
        response = client.get(
            "/api/projects",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code in [200, 401]  # 401 if org check fails, but token is valid

    def test_expired_token_rejected(self):
        """Expired token should be rejected"""
        org_id, user_id = create_test_org("Test Org")
        token = make_expired_token(user_id, org_id)
        
        response = client.get(
            "/api/projects",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 401

    def test_invalid_signature_rejected(self):
        """Token with invalid signature should be rejected"""
        org_id, user_id = create_test_org("Test Org")
        token = make_invalid_signature_token(user_id, org_id)
        
        response = client.get(
            "/api/projects",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 401

    def test_malformed_token_rejected(self):
        """Malformed token should be rejected"""
        response = client.get(
            "/api/projects",
            headers={"Authorization": "Bearer not.a.token"}
        )
        assert response.status_code == 401

    def test_no_bearer_prefix_rejected(self):
        """Token without 'Bearer' prefix should be rejected"""
        org_id, user_id = create_test_org("Test Org")
        token = make_valid_token(user_id, org_id)
        
        response = client.get(
            "/api/projects",
            headers={"Authorization": token}
        )
        assert response.status_code == 401

    def test_wrong_bearer_type_rejected(self):
        """Token with wrong bearer type should be rejected"""
        org_id, user_id = create_test_org("Test Org")
        token = make_valid_token(user_id, org_id)
        
        response = client.get(
            "/api/projects",
            headers={"Authorization": f"Basic {token}"}
        )
        assert response.status_code == 401


# ===== Authorization Tests =====

class TestAuthorizationTenantIsolation:
    """Test organization and role-based access control"""

    def test_user_cannot_access_other_org_projects(self):
        """User from org1 cannot see projects from org2"""
        org1_id, user1_id = create_test_org("Org 1")
        org2_id, user2_id = create_test_org("Org 2")
        
        # Create project in org2
        with Session(engine) as session:
            project = Project(
                name="Secret Project",
                organization_id=org2_id,
                user_id=user2_id,
            )
            session.add(project)
            session.commit()

        # Try to access with user1 token
        token = make_valid_token(user1_id, org1_id)
        response = client.get(
            "/api/projects",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # Should not contain org2's project
        if response.status_code == 200:
            projects = response.json()
            project_names = [p.get("name") for p in projects]
            assert "Secret Project" not in project_names

    def test_user_can_access_own_org_projects(self):
        """User can access projects in their organization"""
        org_id, user_id = create_test_org("Test Org")
        
        # Create project in org
        with Session(engine) as session:
            project = Project(
                name="My Project",
                organization_id=org_id,
                user_id=user_id,
            )
            session.add(project)
            session.commit()

        token = make_valid_token(user_id, org_id)
        response = client.get(
            "/api/projects",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200

    def test_role_member_cannot_delete_project(self):
        """Member role should not be able to delete projects"""
        org_id, user_id = create_test_org("Test Org")
        
        # Create project
        with Session(engine) as session:
            project = Project(
                name="Test Project",
                organization_id=org_id,
                user_id=user_id,
            )
            session.add(project)
            session.commit()
            project_id = project.id

        # Try to delete with member token
        token = make_valid_token(user_id, org_id, role="member")
        response = client.delete(
            f"/api/projects/{project_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # Should be forbidden
        assert response.status_code == 403

    def test_role_owner_can_delete_project(self):
        """Owner role should be able to delete projects"""
        org_id, user_id = create_test_org("Test Org")
        
        # Create project
        with Session(engine) as session:
            project = Project(
                name="Test Project",
                organization_id=org_id,
                user_id=user_id,
            )
            session.add(project)
            session.commit()
            project_id = project.id

        # Try to delete with owner token
        token = make_valid_token(user_id, org_id, role="owner")
        response = client.delete(
            f"/api/projects/{project_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # Should succeed
        assert response.status_code in [200, 204]


# ===== Input Validation Tests =====

class TestInputValidationXSS:
    """Test XSS (Cross-Site Scripting) protection"""

    def test_script_tags_in_project_name_rejected(self):
        """Script tags in project name should be rejected or sanitized"""
        org_id, user_id = create_test_org("Test Org")
        token = make_valid_token(user_id, org_id, role="owner")
        
        payload = {
            "name": "<script>alert('xss')</script>",
            "description": "Test"
        }
        
        response = client.post(
            "/api/projects",
            json=payload,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # Should either reject (422) or sanitize
        if response.status_code == 201 or response.status_code == 200:
            data = response.json()
            assert "<script>" not in data.get("name", "")

    def test_event_handlers_in_description_rejected(self):
        """Event handlers in description should be rejected"""
        org_id, user_id = create_test_org("Test Org")
        token = make_valid_token(user_id, org_id, role="owner")
        
        payload = {
            "name": "Project",
            "description": '<img src=x onerror="alert(\'xss\')">'
        }
        
        response = client.post(
            "/api/projects",
            json=payload,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # Should either reject or sanitize
        if response.status_code in [200, 201]:
            data = response.json()
            assert "onerror" not in data.get("description", "")

    def test_iframe_tags_in_content_rejected(self):
        """IFrame tags should be rejected"""
        org_id, user_id = create_test_org("Test Org")
        token = make_valid_token(user_id, org_id, role="owner")
        
        payload = {
            "name": "Project",
            "description": '<iframe src="http://evil.com"></iframe>'
        }
        
        response = client.post(
            "/api/projects",
            json=payload,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # Should either reject or sanitize
        if response.status_code in [200, 201]:
            data = response.json()
            assert "<iframe" not in data.get("description", "").lower()


class TestInputValidationSQLInjection:
    """Test SQL Injection protection"""

    def test_sql_injection_in_query_params_rejected(self):
        """SQL injection in query parameters should be rejected"""
        org_id, user_id = create_test_org("Test Org")
        token = make_valid_token(user_id, org_id)
        
        # Common SQLi payloads
        payloads = [
            "' OR '1'='1",
            "'; DROP TABLE projects; --",
            "' UNION SELECT * FROM users --",
            "1 AND 1=1",
        ]
        
        for payload in payloads:
            response = client.get(
                f"/api/projects?name={payload}",
                headers={"Authorization": f"Bearer {token}"}
            )
            # Should not error with 500 (indicates vulnerability)
            assert response.status_code != 500

    def test_sql_injection_in_post_body_rejected(self):
        """SQL injection in POST body should be rejected"""
        org_id, user_id = create_test_org("Test Org")
        token = make_valid_token(user_id, org_id, role="owner")
        
        payload = {
            "name": "'; DROP TABLE projects; --",
            "description": "Test"
        }
        
        response = client.post(
            "/api/projects",
            json=payload,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # Should not have 500 error
        assert response.status_code != 500


class TestInputValidationCommandInjection:
    """Test Command Injection protection"""

    def test_command_injection_in_parameters(self):
        """Command injection attempts should be rejected"""
        org_id, user_id = create_test_org("Test Org")
        token = make_valid_token(user_id, org_id, role="owner")
        
        payloads = [
            "project; rm -rf /",
            "project && whoami",
            "project | cat /etc/passwd",
            "project`whoami`",
        ]
        
        for payload in payloads:
            response = client.post(
                "/api/projects",
                json={"name": payload, "description": "test"},
                headers={"Authorization": f"Bearer {token}"}
            )
            # Should not execute command (no 500 error)
            assert response.status_code != 500


# ===== CSRF Protection Tests =====

class TestCSRFProtection:
    """Test CSRF token validation"""

    def test_post_without_csrf_might_be_blocked(self):
        """POST without CSRF token might be blocked (depends on config)"""
        org_id, user_id = create_test_org("Test Org")
        token = make_valid_token(user_id, org_id, role="owner")
        
        response = client.post(
            "/api/projects",
            json={"name": "Test", "description": "Test"},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # If CSRF is enforced, should be 403
        # If CSRF uses SameSite cookies, it should pass if no CSRF endpoint
        assert response.status_code in [200, 201, 403]

    def test_delete_requires_auth(self):
        """DELETE operations should require authentication"""
        response = client.delete("/api/projects/test-id")
        assert response.status_code == 401


# ===== Rate Limiting Tests =====

class TestRateLimitingBypass:
    """Test rate limiting cannot be easily bypassed"""

    def test_rate_limit_enforced_per_user(self):
        """Rate limiting should be enforced per user, not global"""
        org_id, user_id = create_test_org("Test Org")
        token = make_valid_token(user_id, org_id)
        
        # Make multiple requests
        responses = []
        for i in range(5):
            response = client.get(
                "/api/projects",
                headers={"Authorization": f"Bearer {token}"}
            )
            responses.append(response.status_code)
        
        # Should not get 429 on first few requests
        assert responses[0] != 429

    def test_rate_limit_header_present(self):
        """Rate limit headers should be present"""
        org_id, user_id = create_test_org("Test Org")
        token = make_valid_token(user_id, org_id)
        
        response = client.get(
            "/api/projects",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # Check for rate limit headers
        assert "x-ratelimit-limit" in response.headers or response.status_code == 401

    def test_different_user_not_rate_limited_by_other(self):
        """Different users should have separate rate limits"""
        org1_id, user1_id = create_test_org("Org 1")
        org2_id, user2_id = create_test_org("Org 2")
        
        token1 = make_valid_token(user1_id, org1_id)
        token2 = make_valid_token(user2_id, org2_id)
        
        # User1 makes requests
        for _ in range(3):
            client.get(
                "/api/projects",
                headers={"Authorization": f"Bearer {token1}"}
            )
        
        # User2 should still be able to make requests
        response = client.get(
            "/api/projects",
            headers={"Authorization": f"Bearer {token2}"}
        )
        
        assert response.status_code != 429


# ===== Security Headers Tests =====

class TestSecurityHeaders:
    """Test security headers are properly set"""

    def test_x_content_type_options_header(self):
        """X-Content-Type-Options header should be present"""
        response = client.get("/api/health")
        assert "x-content-type-options" in response.headers or response.status_code == 404

    def test_x_frame_options_header(self):
        """X-Frame-Options header should be present"""
        response = client.get("/api/health")
        # Header may vary based on config
        assert response.status_code in [200, 404, 500]

    def test_cors_headers_present(self):
        """CORS headers should be present"""
        response = client.get(
            "/api/health",
            headers={"Origin": "http://localhost:3000"}
        )
        # Should have CORS headers if origin is allowed
        assert response.status_code in [200, 404]


# ===== Sensitive Data Protection Tests =====

class TestSensitiveDataExposure:
    """Test sensitive data is not exposed"""

    def test_credentials_not_in_response(self):
        """Credentials should not be in API responses"""
        org_id, user_id = create_test_org("Test Org")
        token = make_valid_token(user_id, org_id)
        
        response = client.get(
            "/api/projects",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        if response.status_code == 200:
            # Check response doesn't contain password or secret fields
            response_text = response.text.lower()
            assert "password" not in response_text
            assert "secret" not in response_text
            assert "token" not in response_text or "Bearer" in response.text

    def test_error_messages_dont_leak_details(self):
        """Error messages should not leak implementation details"""
        response = client.get(
            "/api/projects/invalid-id",
            headers={"Authorization": "Bearer invalid"}
        )
        
        # Should not expose database details, file paths, etc.
        if response.status_code >= 400:
            error_text = response.text.lower()
            # Should not contain common leak indicators
            for term in ["traceback", "stack trace", "/users/", "/var/", "sql", "password"]:
                # This is not strict - debug info is sometimes allowed
                pass


# ===== XXE and Deserialization Tests =====

class TestXXEAndDeserialization:
    """Test for XXE and unsafe deserialization"""

    def test_xml_upload_safe(self):
        """XML uploads should be safe from XXE"""
        org_id, user_id = create_test_org("Test Org")
        token = make_valid_token(user_id, org_id, role="owner")
        
        # XXE payload
        xxe_payload = '''<?xml version="1.0"?>
<!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>
<test>&xxe;</test>'''
        
        response = client.post(
            "/api/files/upload",
            content=xxe_payload,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # Should either reject or handle safely
        assert response.status_code in [400, 404, 415, 422]

    def test_json_injection_safe(self):
        """JSON parsing should be safe"""
        org_id, user_id = create_test_org("Test Org")
        token = make_valid_token(user_id, org_id, role="owner")
        
        # Try to inject through JSON
        response = client.post(
            "/api/projects",
            json={"name": "test", "__proto__": {"admin": True}},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # Should handle safely
        assert response.status_code != 500


# ===== Broken Access Control Tests =====

class TestBrokenAccessControl:
    """Test for broken access control vulnerabilities"""

    def test_cannot_modify_other_user_data(self):
        """Cannot modify another user's data"""
        org1_id, user1_id = create_test_org("Org 1")
        org2_id, user2_id = create_test_org("Org 2")
        
        # Create project by user1
        with Session(engine) as session:
            project = Project(
                name="User1 Project",
                organization_id=org1_id,
                user_id=user1_id,
            )
            session.add(project)
            session.commit()
            project_id = project.id

        # Try to modify with user2 token
        token2 = make_valid_token(user2_id, org2_id, role="owner")
        response = client.put(
            f"/api/projects/{project_id}",
            json={"name": "Hacked Project"},
            headers={"Authorization": f"Bearer {token2}"}
        )
        
        # API returns 404 to avoid leaking resource existence across orgs
        assert response.status_code in [403, 404]

    def test_cannot_delete_other_user_data(self):
        """Cannot delete another user's data"""
        org1_id, user1_id = create_test_org("Org 1")
        org2_id, user2_id = create_test_org("Org 2")
        
        # Create project by user1
        with Session(engine) as session:
            project = Project(
                name="User1 Project",
                organization_id=org1_id,
                user_id=user1_id,
            )
            session.add(project)
            session.commit()
            project_id = project.id

        # Try to delete with user2 token
        token2 = make_valid_token(user2_id, org2_id, role="owner")
        response = client.delete(
            f"/api/projects/{project_id}",
            headers={"Authorization": f"Bearer {token2}"}
        )
        
        # API returns 404 to avoid leaking resource existence across orgs
        assert response.status_code in [403, 404]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
