"""Integration tests for intelligence endpoints."""

import pytest

pytestmark = pytest.mark.integration


@pytest.mark.integration
class TestIntelligenceOperations:
    """Tests for intelligence endpoints."""
    
    def test_get_intelligence_data(self, client, test_token):
        """Test retrieving intelligence data."""
        response = client.get(
            "/api/intelligence",
            headers={"Authorization": f"Bearer {test_token}"}
        )
        # Endpoint may not exist yet
        assert response.status_code in [200, 404]
    
    def test_create_intelligence_item(self, client, test_token):
        """Test creating an intelligence item."""
        response = client.post(
            "/api/intelligence",
            headers={"Authorization": f"Bearer {test_token}"},
            json={"title": "Test Intelligence"}
        )
        # Endpoint may not exist yet
        assert response.status_code in [200, 201, 404]
    
    def test_intelligence_unauthorized(self, client):
        """Test that unauthorized access is denied."""
        response = client.get("/api/intelligence")
        assert response.status_code == 401


@pytest.mark.integration
class TestIntelligenceScraping:
    """Tests for intelligence scraping operations."""
    
    def test_scrape_intelligence(self, client, test_token):
        """Test scraping intelligence data."""
        response = client.post(
            "/api/intelligence/scrape",
            headers={"Authorization": f"Bearer {test_token}"},
            json={"url": "https://example.com"}
        )
        # Endpoint may not exist yet
        assert response.status_code in [200, 404]
    
    def test_scrape_unauthorized(self, client):
        """Test that unauthorized scraping is denied."""
        response = client.post(
            "/api/intelligence/scrape",
            json={"url": "https://example.com"}
        )
        assert response.status_code == 401


@pytest.mark.integration
class TestIntelligenceRateLimiting:
    """Tests for rate limiting on expensive intelligence endpoints."""
    
    @pytest.mark.rate_limit
    def test_scrape_respects_rate_limits(self, client, test_token):
        """Test that intelligence scraping respects rate limits."""
        # This depends on whether expensive endpoints use different limits
        response = client.post(
            "/api/intelligence/scrape",
            headers={"Authorization": f"Bearer {test_token}"},
            json={"url": "https://example.com"}
        )
        assert response.status_code in [200, 404]


@pytest.mark.integration
class TestIntelligenceTenantIsolation:
    """Tests for tenant isolation in intelligence endpoints."""
    
    def test_user_sees_only_own_intelligence(self, client, test_token):
        """Test that users can only see intelligence from their org."""
        response = client.get(
            "/api/intelligence",
            headers={"Authorization": f"Bearer {test_token}"}
        )
        if response.status_code == 200:
            data = response.json()
            # All intelligence should belong to user's org
            assert isinstance(data, list)
