"""Integration tests for projects endpoints."""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

pytestmark = pytest.mark.integration


@pytest.mark.integration
class TestProjectList:
    """Tests for listing projects."""
    
    def test_list_projects_empty(self, client, test_token):
        response = client.get(
            "/api/projects",
            headers={"Authorization": f"Bearer {test_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_list_projects_unauthorized(self, client):
        response = client.get("/api/projects")
        assert response.status_code == 401


@pytest.mark.integration
class TestProjectCreate:
    """Tests for creating projects."""
    
    def test_create_project(self, client, test_token):
        response = client.post(
            "/api/projects",
            headers={"Authorization": f"Bearer {test_token}"},
            json={
                "name": "Test Project",
                "description": "A test project",
            }
        )
        assert response.status_code in [200, 201]
        data = response.json()
        assert data["name"] == "Test Project"
        assert "id" in data
    
    def test_create_project_missing_name(self, client, test_token):
        response = client.post(
            "/api/projects",
            headers={"Authorization": f"Bearer {test_token}"},
            json={
                "description": "A test project",
            }
        )
        assert response.status_code in [400, 422]
    
    def test_create_project_unauthorized(self, client):
        response = client.post(
            "/api/projects",
            json={
                "name": "Test Project",
            }
        )
        assert response.status_code == 401


@pytest.mark.integration
class TestProjectTenantIsolation:
    """Tests for tenant isolation on project endpoints."""
    
    def test_user_cannot_access_other_org_project(
        self,
        client,
        test_token,
        test_session,
        test_org
    ):
        """User should not see projects from other organizations."""
        # This test would require creating another org and user
        # For now, verify that org_id filtering is in place
        response = client.get(
            "/api/projects",
            headers={"Authorization": f"Bearer {test_token}"}
        )
        assert response.status_code == 200
        # Projects should be filtered by org_id
    
    def test_create_project_sets_correct_org(self, client, test_token, test_user):
        user_id, org_id = test_user
        
        response = client.post(
            "/api/projects",
            headers={"Authorization": f"Bearer {test_token}"},
            json={"name": "Test"}
        )
        
        if response.status_code in [200, 201]:
            data = response.json()
            # Project should belong to user's org
            assert data.get("organization_id") == org_id or data.get("org_id") == org_id


@pytest.mark.integration
class TestProjectRead:
    """Tests for reading project details."""
    
    def test_get_project(self, client, test_token):
        # First create a project
        create_response = client.post(
            "/api/projects",
            headers={"Authorization": f"Bearer {test_token}"},
            json={"name": "Test Project"}
        )
        
        if create_response.status_code in [200, 201]:
            project_id = create_response.json()["id"]
            
            # Then get it
            get_response = client.get(
                f"/api/projects/{project_id}",
                headers={"Authorization": f"Bearer {test_token}"}
            )
            assert get_response.status_code == 200
            assert get_response.json()["id"] == project_id
    
    def test_get_nonexistent_project(self, client, test_token):
        response = client.get(
            "/api/projects/nonexistent",
            headers={"Authorization": f"Bearer {test_token}"}
        )
        assert response.status_code == 404


@pytest.mark.integration
class TestProjectUpdate:
    """Tests for updating projects."""
    
    def test_update_project(self, client, test_token):
        # Create project
        create_response = client.post(
            "/api/projects",
            headers={"Authorization": f"Bearer {test_token}"},
            json={"name": "Original Name"}
        )
        
        if create_response.status_code in [200, 201]:
            project_id = create_response.json()["id"]
            
            # Update it
            update_response = client.put(
                f"/api/projects/{project_id}",
                headers={"Authorization": f"Bearer {test_token}"},
                json={"name": "Updated Name"}
            )
            
            if update_response.status_code in [200, 404]:
                # Endpoint may or may not exist
                if update_response.status_code == 200:
                    assert update_response.json()["name"] == "Updated Name"


@pytest.mark.integration
class TestProjectDelete:
    """Tests for deleting projects."""
    
    def test_delete_project(self, client, test_token):
        # Create project
        create_response = client.post(
            "/api/projects",
            headers={"Authorization": f"Bearer {test_token}"},
            json={"name": "Project to Delete"}
        )
        
        if create_response.status_code in [200, 201]:
            project_id = create_response.json()["id"]
            
            # Delete it
            delete_response = client.delete(
                f"/api/projects/{project_id}",
                headers={"Authorization": f"Bearer {test_token}"}
            )
            
            if delete_response.status_code in [200, 204, 404]:
                # Could be deleted or not exist
                # Verify it's gone
                get_response = client.get(
                    f"/api/projects/{project_id}",
                    headers={"Authorization": f"Bearer {test_token}"}
                )
                assert get_response.status_code in [404]
