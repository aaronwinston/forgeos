import pytest
from datetime import datetime, timedelta, timezone

from models import CalendarIntegration, CalendarSyncLog, Membership, Organization

pytestmark = pytest.mark.integration

import personal_mode as _personal_mode_test_integrations_isolation
from config import settings as _settings_test_integrations_isolation


@pytest.fixture(autouse=True, scope="module")
def _enable_multi_tenant_test_integrations_isolation():
    """Force multi-tenant mode so JWT auth is enforced."""
    original_mode = _settings_test_integrations_isolation.FORGEOS_MODE
    original_fn = _personal_mode_test_integrations_isolation.is_personal
    _settings_test_integrations_isolation.FORGEOS_MODE = "multi_tenant"
    _personal_mode_test_integrations_isolation.is_personal = lambda: False
    yield
    _settings_test_integrations_isolation.FORGEOS_MODE = original_mode
    _personal_mode_test_integrations_isolation.is_personal = original_fn




def _auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_google_status_is_scoped_to_auth_org(client, test_session, test_org, test_token):
    other_org = Organization(id="test-org-2", name="Other Org", slug="other-org")
    test_session.add(other_org)
    test_session.add(
        Membership(
            id="test-member-2",
            user_id="other-user",
            organization_id=other_org.id,
            role="owner",
        )
    )

    other_integration = CalendarIntegration(
        organization_id=other_org.id,
        user_id="aaron",
        expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
        calendar_id="other-calendar",
    )
    other_integration.access_token = "other-access"
    other_integration.refresh_token = "other-refresh"
    test_session.add(other_integration)
    test_session.commit()

    response = client.get(
        "/api/integrations/google/status",
        headers=_auth_headers(test_token),
    )
    assert response.status_code == 200
    assert response.json()["connected"] is False


def test_google_sync_status_error_list_is_org_scoped(client, test_session, test_org, test_token):
    expires_at = datetime.now(timezone.utc) + timedelta(hours=1)

    integration = CalendarIntegration(
        organization_id=test_org.id,
        user_id="test-user-1",
        expires_at=expires_at,
        calendar_id="org1-calendar",
    )
    integration.access_token = "org1-access"
    integration.refresh_token = "org1-refresh"
    test_session.add(integration)

    other_org = Organization(id="test-org-3", name="Other Org 3", slug="other-org-3")
    test_session.add(other_org)
    other_integration = CalendarIntegration(
        organization_id=other_org.id,
        user_id="aaron",
        expires_at=expires_at,
        calendar_id="org3-calendar",
    )
    other_integration.access_token = "org3-access"
    other_integration.refresh_token = "org3-refresh"
    test_session.add(other_integration)
    test_session.commit()

    test_session.add(
        CalendarSyncLog(
            organization_id=other_org.id,
            operation="poll",
            status="error",
            error_message="other-org-error",
        )
    )
    test_session.add(
        CalendarSyncLog(
            organization_id=test_org.id,
            operation="poll",
            status="error",
            error_message="own-org-error",
        )
    )
    test_session.commit()

    response = client.get(
        "/api/integrations/google/sync-status",
        headers=_auth_headers(test_token),
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["connected"] is True
    assert payload["errors_last_sync"][0]["error"] == "own-org-error"


def test_sync_now_forwards_auth_org_to_poll(monkeypatch, client, test_token):
    captured = {}

    def fake_poll_from_google(organization_id=None):
        captured["organization_id"] = organization_id
        return {"status": "success", "updated_count": 0, "archived_count": 0, "errors": []}

    monkeypatch.setattr("services.calendar.poll_from_google", fake_poll_from_google)

    response = client.post(
        "/api/integrations/google/sync-now",
        headers={
            **_auth_headers(test_token),
            "X-CSRF-Token": "x" * 32,
        },
    )
    assert response.status_code == 200
    assert captured["organization_id"] == "test-org-1"
