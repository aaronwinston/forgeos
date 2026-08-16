import pytest
from fastapi import HTTPException
from pydantic import ValidationError

from middleware.auth import AuthContext
from models import Deliverable, Folder, Membership, Organization, Project
from routers.projects import (
    ConversionOutcomeSnapshotCreate,
    ConversionTaxonomyCreate,
    DeliverableCTAExperimentCreate,
    create_conversion_outcome_snapshot,
    create_conversion_taxonomy_definition,
    create_deliverable_cta_experiment,
    get_deliverable_conversion_loop,
)

pytestmark = pytest.mark.integration


def _create_deliverable(test_session, organization_id: str, user_id: str, title: str) -> Deliverable:
    project = Project(user_id=user_id, organization_id=organization_id, name=f"Project {title}")
    test_session.add(project)
    test_session.commit()
    test_session.refresh(project)

    folder = Folder(project_id=project.id, organization_id=organization_id, name=f"Folder {title}")
    test_session.add(folder)
    test_session.commit()
    test_session.refresh(folder)

    deliverable = Deliverable(
        folder_id=folder.id,
        organization_id=organization_id,
        content_type="blog",
        title=title,
    )
    test_session.add(deliverable)
    test_session.commit()
    test_session.refresh(deliverable)
    return deliverable


def test_conversion_loop_write_and_read_behavior(test_session, test_user):
    user_id, org_id = test_user
    auth = AuthContext(user_id=user_id, org_id=org_id, role="member")
    deliverable = _create_deliverable(test_session, org_id, user_id, "Conversion loop")

    taxonomy = create_conversion_taxonomy_definition(
        deliverable_id=deliverable.id,
        payload=ConversionTaxonomyCreate(
            event_key="signup_click",
            funnel_stage="consideration",
            definition="User clicked signup CTA",
            primary_cta="Start free",
            success_metric="signup_rate",
        ),
        auth=auth,
        session=test_session,
    )
    assert taxonomy["event_key"] == "signup_click"

    outcome = create_conversion_outcome_snapshot(
        deliverable_id=deliverable.id,
        payload=ConversionOutcomeSnapshotCreate(
            period_label="2026-W33",
            visitors=100,
            conversions=9,
            conversion_rate=0.09,
            observed_outcome="Variant A performed better",
            notes="Manual weekly update",
        ),
        auth=auth,
        session=test_session,
    )
    assert outcome["period_label"] == "2026-W33"

    cta = create_deliverable_cta_experiment(
        deliverable_id=deliverable.id,
        payload=DeliverableCTAExperimentCreate(
            experiment_key="homepage_signup",
            variant_label="A",
            status="active",
            conversion_rate=0.12,
            observed_outcome="A above baseline",
        ),
        auth=auth,
        session=test_session,
    )
    assert cta["variant_label"] == "A"

    payload = get_deliverable_conversion_loop(
        deliverable_id=deliverable.id,
        auth=auth,
        session=test_session,
    )

    assert payload["deliverable_id"] == deliverable.id
    assert payload["content_type"] == "blog"
    assert len(payload["taxonomy_definitions"]) == 1
    assert payload["taxonomy_definitions"][0]["event_key"] == "signup_click"
    assert len(payload["conversion_outcomes"]) == 1
    assert payload["conversion_outcomes"][0]["period_label"] == "2026-W33"
    assert len(payload["cta_experiments"]) == 1
    assert payload["cta_experiments"][0]["variant_label"] == "A"


def test_conversion_loop_enforces_org_isolation(test_session, test_user):
    user_id, org_id = test_user
    auth = AuthContext(user_id=user_id, org_id=org_id, role="member")
    own_deliverable = _create_deliverable(test_session, org_id, user_id, "Own deliverable")

    other_org = Organization(id="test-org-2", name="Other Org", slug="other-org")
    test_session.add(other_org)
    test_session.add(
        Membership(
            id="test-member-other",
            user_id="other-user",
            organization_id=other_org.id,
            role="owner",
        )
    )
    test_session.commit()
    other_deliverable = _create_deliverable(test_session, other_org.id, "other-user", "Other deliverable")

    with pytest.raises(HTTPException) as read_exc:
        get_deliverable_conversion_loop(
            deliverable_id=other_deliverable.id,
            auth=auth,
            session=test_session,
        )
    assert read_exc.value.status_code == 404

    with pytest.raises(HTTPException) as write_exc:
        create_conversion_taxonomy_definition(
            deliverable_id=other_deliverable.id,
            payload=ConversionTaxonomyCreate(
                event_key="forbidden",
                funnel_stage="awareness",
                definition="Should fail",
            ),
            auth=auth,
            session=test_session,
        )
    assert write_exc.value.status_code == 404

    own_loop = get_deliverable_conversion_loop(
        deliverable_id=own_deliverable.id,
        auth=auth,
        session=test_session,
    )
    assert own_loop["taxonomy_definitions"] == []
    assert own_loop["conversion_outcomes"] == []
    assert own_loop["cta_experiments"] == []


def test_conversion_loop_validation_models():
    with pytest.raises(ValidationError):
        ConversionTaxonomyCreate(
            event_key="Invalid Key",
            funnel_stage="awareness",
            definition="Bad key",
        )

    with pytest.raises(ValidationError):
        ConversionOutcomeSnapshotCreate(
            period_label="2026-W33",
            conversion_rate=1.5,
        )

    with pytest.raises(ValidationError):
        DeliverableCTAExperimentCreate(
            experiment_key="homepage_signup",
            variant_label="B",
            status="running",
        )
