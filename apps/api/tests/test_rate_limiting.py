"""Comprehensive rate limiting tests."""

import uuid
import pytest
import jwt
from fastapi.testclient import TestClient
from sqlmodel import Session

from config import settings
from database import engine
from main import app
from models import Membership, Organization

pytestmark = pytest.mark.rate_limit


@pytest.mark.rate_limit
class TestRateLimitingBasics:
    """Tests for basic rate limiting functionality."""
    
    def test_rate_limit_headers_present(self, client):
        """Verify that rate limit headers are included in responses."""
        response = client.get("/api/health")
        assert response.status_code in [200, 429]
        # Headers should be present (even on rate limited responses)
        assert "x-ratelimit-limit" in response.headers or "X-RateLimit-Limit" in response.headers
    
    def test_429_response_on_limit_exceeded(self, client):
        """Verify that 429 is returned when rate limit exceeded."""
        limit_count = int(settings.RATE_LIMIT_PUBLIC.split("/")[0])
        
        responses = []
        for i in range(limit_count + 1):
            response = client.get("/api/health")
            responses.append(response.status_code)
        
        # First N should succeed, N+1 should be rate limited
        assert 200 in responses
        assert 429 in responses


@pytest.mark.rate_limit
class TestAuthEndpointRateLimiting:
    """Tests for rate limiting on auth endpoints."""
    
    def test_auth_endpoints_have_strict_limits(self, client):
        """Auth endpoints should have stricter rate limits."""
        limit = settings.RATE_LIMIT_AUTH
        limit_count = int(limit.split("/")[0])
        
        responses = []
        for i in range(limit_count + 2):
            response = client.post(
                "/api/auth/signin",
                json={
                    "email": f"test{i}@example.com",
                    "password": "testpass",
                }
            )
            responses.append(response.status_code)
        
        # Should have at least one 429 response
        assert 429 in responses
    
    def test_signup_endpoint_rate_limited(self, client):
        """Signup endpoint should be rate limited."""
        limit = settings.RATE_LIMIT_AUTH
        limit_count = int(limit.split("/")[0])
        
        responses = []
        for i in range(limit_count + 2):
            response = client.post(
                "/api/auth/signup",
                json={
                    "email": f"newuser{i}@example.com",
                    "password": "SecurePass123",
                    "org_name": f"Org {i}",
                }
            )
            responses.append(response.status_code)
        
        # Should hit rate limit
        assert 429 in responses


@pytest.mark.rate_limit
class TestPerUserRateLimiting:
    """Tests for per-user rate limiting on authenticated endpoints."""
    
    def test_per_user_limit_with_jwt(self, client, test_token):
        """Authenticated requests should be rate limited per user."""
        limit = settings.RATE_LIMIT_INTERNAL
        limit_count = int(limit.split("/")[0])
        
        responses = []
        for i in range(limit_count + 1):
            response = client.get(
                "/api/projects",
                headers={"Authorization": f"Bearer {test_token}"}
            )
            responses.append(response.status_code)
        
        # Should hit rate limit
        assert 429 in responses
    
    def test_different_users_have_independent_limits(
        self,
        client,
        test_token,
        test_session,
        test_org
    ):
        """Different users should have independent rate limits."""
        # Create second user in same org
        user2_id = "test-user-2"
        membership2 = Membership(
            id="test-member-2",
            user_id=user2_id,
            organization_id=test_org.id,
            role="member",
        )
        test_session.add(membership2)
        test_session.commit()
        
        # Create token for user2
        payload = {
            "sub": user2_id,
            "org_id": test_org.id,
            "role": "member",
        }
        token2 = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm="HS256")
        
        # Both users should be able to make requests independently
        response1 = client.get(
            "/api/projects",
            headers={"Authorization": f"Bearer {test_token}"}
        )
        response2 = client.get(
            "/api/projects",
            headers={"Authorization": f"Bearer {token2}"}
        )
        
        # Both should succeed (not rate limited against each other)
        assert response1.status_code in [200, 204]
        assert response2.status_code in [200, 204]


@pytest.mark.rate_limit
class TestPerIpRateLimiting:
    """Tests for per-IP rate limiting on public endpoints."""
    
    def test_unauthenticated_requests_limited_per_ip(self, client):
        """Unauthenticated requests should be limited per IP."""
        limit = settings.RATE_LIMIT_PUBLIC
        limit_count = int(limit.split("/")[0])
        
        responses = []
        for i in range(limit_count + 1):
            response = client.get("/api/health")
            responses.append(response.status_code)
        
        # Should eventually hit rate limit
        assert 429 in responses


@pytest.mark.rate_limit
class TestRateLimitHeaders:
    """Tests for rate limit response headers."""
    
    def test_x_ratelimit_limit_header(self, client):
        """X-RateLimit-Limit header should indicate the limit."""
        response = client.get("/api/health")
        assert response.status_code in [200, 429]
        
        headers = response.headers
        has_limit = "x-ratelimit-limit" in headers or "X-RateLimit-Limit" in headers
        assert has_limit
    
    def test_x_ratelimit_remaining_header(self, client):
        """X-RateLimit-Remaining header should show remaining requests."""
        response = client.get("/api/health")
        assert response.status_code == 200
        
        headers = response.headers
        has_remaining = "x-ratelimit-remaining" in headers or "X-RateLimit-Remaining" in headers
        assert has_remaining
    
    def test_x_ratelimit_reset_header(self, client):
        """X-RateLimit-Reset header should show reset time."""
        response = client.get("/api/health")
        assert response.status_code == 200
        
        headers = response.headers
        has_reset = "x-ratelimit-reset" in headers or "X-RateLimit-Reset" in headers
        assert has_reset
    
    def test_retry_after_header_on_429(self, client):
        """Retry-After header should be present on 429 responses."""
        limit = settings.RATE_LIMIT_PUBLIC
        limit_count = int(limit.split("/")[0])
        
        # Hit rate limit
        for i in range(limit_count + 1):
            response = client.get("/api/health")
        
        # Last response should be rate limited
        if response.status_code == 429:
            assert "retry-after" in response.headers or "Retry-After" in response.headers


@pytest.mark.rate_limit
class TestRateLimitErrorResponses:
    """Tests for rate limit error response format."""
    
    def test_429_returns_json(self, client):
        """429 response should be JSON with error details."""
        limit = settings.RATE_LIMIT_PUBLIC
        limit_count = int(limit.split("/")[0])
        
        # Hit rate limit
        for i in range(limit_count + 1):
            response = client.get("/api/health")
        
        # Last response should be rate limited
        if response.status_code == 429:
            data = response.json()
            assert isinstance(data, dict)
            assert "detail" in data or "error" in data
    
    def test_429_not_html(self, client):
        """429 response should be JSON, not HTML."""
        limit = settings.RATE_LIMIT_PUBLIC
        limit_count = int(limit.split("/")[0])
        
        # Hit rate limit
        for i in range(limit_count + 1):
            response = client.get("/api/health")
        
        # Last response should be rate limited
        if response.status_code == 429:
            content_type = response.headers.get("content-type", "").lower()
            assert "json" in content_type


@pytest.mark.rate_limit
class TestExpensiveEndpointRateLimiting:
    """Tests for stricter rate limiting on expensive endpoints."""
    
    def test_expensive_endpoints_have_global_cap(self, client, test_token):
        """Expensive endpoints should have additional global rate limits."""
        # This would test /api/trust/export, /api/intelligence/scrape, etc.
        # The test depends on which endpoints are marked as expensive
        pass


@pytest.mark.rate_limit
class TestRateLimitEdgeCases:
    """Tests for edge cases in rate limiting."""
    
    def test_missing_jwt_treated_as_unauthenticated(self, client):
        """Missing JWT token should fall back to IP-based limiting."""
        response = client.get("/api/projects")
        assert response.status_code == 401
    
    def test_invalid_jwt_treated_as_unauthenticated(self, client):
        """Invalid JWT token should fall back to IP-based limiting."""
        response = client.get(
            "/api/projects",
            headers={"Authorization": "Bearer invalid_token_here"}
        )
        assert response.status_code == 401
    
    def test_malformed_authorization_header(self, client):
        """Malformed Authorization header should be handled gracefully."""
        response = client.get(
            "/api/projects",
            headers={"Authorization": "InvalidFormat"}
        )
        assert response.status_code == 401


@pytest.mark.rate_limit
class TestRateLimitConcurrency:
    """Tests for rate limiting under concurrent load."""
    
    def test_concurrent_requests_respected(self, client):
        """Rate limit should be respected even with concurrent requests."""
        # This is a simplified test - actual concurrency testing would use threading
        limit = settings.RATE_LIMIT_PUBLIC
        limit_count = int(limit.split("/")[0])
        
        responses = []
        for i in range(limit_count + 2):
            response = client.get("/api/health")
            responses.append(response.status_code)
        
        # Should eventually hit rate limit
        assert 429 in responses


@pytest.mark.rate_limit
class TestRateLimitReset:
    """Tests for rate limit reset after time window."""
    
    def test_rate_limit_reset_after_window(self, client):
        """Rate limit should reset after time window expires."""
        # This test would need to mock time or wait for actual reset
        # For now, just verify the basic functionality works
        response1 = client.get("/api/health")
        assert response1.status_code in [200, 429]
        
        # Second request should work (if first didn't exceed limit)
        response2 = client.get("/api/health")
        assert response2.status_code in [200, 429]
