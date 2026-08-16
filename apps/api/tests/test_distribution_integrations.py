from models import DistributionIntegrationTarget, Membership, Organization


def _auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_create_and_list_distribution_targets_are_org_scoped(client, test_session, test_org, test_token):
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
    test_session.add(
        DistributionIntegrationTarget(
            organization_id=other_org.id,
            created_by_user_id="other-user",
            channel_type="cms",
            target_key="other-wordpress",
            display_name="Other WordPress",
            endpoint_url="https://cms.other.example/api",
            delivery_mode="scheduled",
            enabled=True,
            preferences_json='{"publish_path":"/blog","content_format":"markdown"}',
        )
    )
    test_session.commit()

    create_response = client.post(
        "/api/integrations/targets",
        headers={**_auth_headers(test_token), "X-CSRF-Token": "x" * 32},
        json={
            "channel_type": "cms",
            "target_key": "wordpress-main",
            "display_name": "Main WordPress",
            "endpoint_url": "https://cms.example.com/api",
            "delivery_mode": "scheduled",
            "enabled": True,
            "preferences": {"publish_path": "/newsroom", "content_format": "markdown"},
        },
    )
    assert create_response.status_code == 200
    created = create_response.json()
    assert created["organization_id"] == test_org.id

    list_response = client.get(
        "/api/integrations/targets",
        headers=_auth_headers(test_token),
    )
    assert list_response.status_code == 200
    payload = list_response.json()
    assert len(payload) == 1
    assert payload[0]["target_key"] == "wordpress-main"


def test_update_distribution_target_cannot_cross_org_boundary(
    client, test_session, test_org, test_token
):
    other_org = Organization(id="test-org-3", name="Other Org 3", slug="other-org-3")
    test_session.add(other_org)
    target = DistributionIntegrationTarget(
        organization_id=other_org.id,
        created_by_user_id="other-user",
        channel_type="crm",
        target_key="hubspot-main",
        display_name="HubSpot Main",
        endpoint_url="https://api.hubapi.com",
        delivery_mode="manual",
        enabled=True,
        preferences_json='{"object_type":"contact","pipeline_stage":"qualified"}',
    )
    test_session.add(target)
    test_session.commit()

    response = client.put(
        f"/api/integrations/targets/{target.id}",
        headers={**_auth_headers(test_token), "X-CSRF-Token": "x" * 32},
        json={
            "channel_type": "crm",
            "target_key": "hubspot-main",
            "display_name": "Should Not Update",
            "endpoint_url": "https://api.hubapi.com",
            "delivery_mode": "manual",
            "enabled": False,
            "preferences": {"object_type": "contact", "pipeline_stage": "qualified"},
        },
    )
    assert response.status_code == 404


def test_distribution_target_validation_requires_cms_and_crm_fields(client, test_token):
    cms_response = client.post(
        "/api/integrations/targets",
        headers={**_auth_headers(test_token), "X-CSRF-Token": "x" * 32},
        json={
            "channel_type": "cms",
            "target_key": "invalid-cms",
            "display_name": "Invalid CMS",
            "endpoint_url": "https://cms.example.com/api",
            "delivery_mode": "scheduled",
            "enabled": True,
            "preferences": {"content_format": "markdown"},
        },
    )
    assert cms_response.status_code == 422
    assert "publish_path" in cms_response.json()["detail"]

    crm_response = client.post(
        "/api/integrations/targets",
        headers={**_auth_headers(test_token), "X-CSRF-Token": "x" * 32},
        json={
            "channel_type": "crm",
            "target_key": "invalid-crm",
            "display_name": "Invalid CRM",
            "endpoint_url": "https://api.hubapi.com",
            "delivery_mode": "manual",
            "enabled": True,
            "preferences": {"object_type": "contact"},
        },
    )
    assert crm_response.status_code == 422
    assert "pipeline_stage" in crm_response.json()["detail"]
