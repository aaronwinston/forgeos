import json

import pytest
from fastapi import HTTPException

from middleware.auth import AuthContext
from models import Deliverable, Folder, Project
from routers.projects import get_deliverable_publish_bundle
from services.publishing import build_publish_payload


def test_build_publish_payload_is_deterministic_and_normalized():
    deliverable = Deliverable(
        id=42,
        organization_id="org-1",
        folder_id=1,
        content_type="blog",
        title="  Arize Launch: Deterministic Publishing!  ",
        body_md="Hello   world\n\nThis is markdown.",
        metadata_json=json.dumps(
            {
                "tags": ["ML", "ml", "  Observability "],
                "slug": "Custom  Slug -- V1",
                "schema_metadata": {"b": 2, "a": {"z": "  x  "}},
                "cta_blocks": [{"label": "  Try now ", "url": "https://arize.com"}],
            }
        ),
    )

    first = build_publish_payload(deliverable).dict()
    second = build_publish_payload(deliverable).dict()

    assert first == second
    assert first["slug"] == "custom-slug-v1"
    assert first["tags"] == ["ml", "observability"]
    assert first["schema_metadata"] == {"a": {"z": "x"}, "b": 2}
    assert first["cta_blocks"] == [{"label": "Try now", "url": "https://arize.com"}]


def test_publish_bundle_endpoint_reflects_approval_gates(test_session, test_user):
    user_id, org_id = test_user
    auth = AuthContext(user_id=user_id, org_id=org_id, role="member")

    project = Project(user_id=user_id, organization_id=org_id, name="P")
    test_session.add(project)
    test_session.commit()
    test_session.refresh(project)

    folder = Folder(project_id=project.id, organization_id=org_id, name="F")
    test_session.add(folder)
    test_session.commit()
    test_session.refresh(folder)

    deliverable = Deliverable(
        folder_id=folder.id,
        organization_id=org_id,
        content_type="blog",
        title="Publishable content",
        body_md="Body for publishing",
        metadata_json=json.dumps(
            {
                "requires_claims_review": True,
                "claims_review_approved": False,
                "tags": ["AI", "ai"],
                "canonical_url": "https://arize.com/blog/example",
            }
        ),
    )
    test_session.add(deliverable)
    test_session.commit()
    test_session.refresh(deliverable)

    response = get_deliverable_publish_bundle(
        deliverable_id=deliverable.id,
        platform="wordpress",
        auth=auth,
        session=test_session,
    )
    data = response.dict()
    second_data = get_deliverable_publish_bundle(
        deliverable_id=deliverable.id,
        platform="wordpress",
        auth=auth,
        session=test_session,
    ).dict()
    assert data == second_data
    assert data["platform"] == "wordpress"
    assert data["payload"]["tags"] == ["ai"]
    assert data["payload"]["approval"]["can_publish"] is False
    assert data["payload"]["approval"]["blocking_reasons"] == ["claims_review_pending"]
    assert data["adapter_payload"]["status"] == "draft"
    assert data["adapter_payload"]["content"] == "Body for publishing"


def test_publish_bundle_endpoint_rejects_unknown_platform(test_session, test_user):
    user_id, org_id = test_user
    auth = AuthContext(user_id=user_id, org_id=org_id, role="member")

    project = Project(user_id=user_id, organization_id=org_id, name="P")
    test_session.add(project)
    test_session.commit()

    folder = Folder(project_id=project.id, organization_id=org_id, name="F")
    test_session.add(folder)
    test_session.commit()
    test_session.refresh(folder)

    deliverable = Deliverable(
        folder_id=folder.id,
        organization_id=org_id,
        content_type="blog",
        title="Platform test",
    )
    test_session.add(deliverable)
    test_session.commit()
    test_session.refresh(deliverable)

    with pytest.raises(HTTPException) as exc:
        get_deliverable_publish_bundle(
            deliverable_id=deliverable.id,
            platform="ghost",
            auth=auth,
            session=test_session,
        )
    assert exc.value.status_code == 400
    assert "Unsupported publishing platform" in str(exc.value.detail)
