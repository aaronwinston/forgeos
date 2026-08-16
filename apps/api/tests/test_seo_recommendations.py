from datetime import datetime, timedelta, timezone

import pytest
from fastapi import HTTPException

from middleware.auth import AuthContext
from models import KeywordCluster, Organization, SearchInsight
from routers.intelligence import get_search_recommendations, seed_brief_from_search_recommendation

pytestmark = pytest.mark.integration


def test_search_recommendations_include_intent_and_movement(test_session, test_user):
    user_id, org_id = test_user
    now = datetime.now(timezone.utc)

    test_session.add(
        KeywordCluster(
            organization_id=org_id,
            user_id=user_id,
            keyword="llm evaluation framework",
            region="US",
            active=True,
        )
    )

    test_session.add_all(
        [
            SearchInsight(
                organization_id=org_id,
                user_id=user_id,
                topic="LLM evaluation framework",
                source_item_ids="1",
                our_gsc_position=11.0,
                our_gsc_clicks=35,
                trends_momentum="rising",
                insight_text="Strong demand for practical evaluation workflows.",
                generated_at=now,
            ),
            SearchInsight(
                organization_id=org_id,
                user_id=user_id,
                topic="LLM evaluation framework",
                source_item_ids="2",
                our_gsc_position=18.0,
                our_gsc_clicks=20,
                trends_momentum="rising",
                insight_text="Earlier baseline snapshot.",
                generated_at=now - timedelta(days=14),
            ),
        ]
    )

    other_org = Organization(id="other-org", name="Other Org", slug="other-org")
    test_session.add(other_org)
    test_session.add(
        SearchInsight(
            organization_id=other_org.id,
            user_id="other-user",
            topic="Should not leak",
            source_item_ids="3",
            trends_momentum="rising",
            insight_text="Other org insight",
            generated_at=now,
        )
    )
    test_session.commit()

    response = get_search_recommendations(
        auth=AuthContext(user_id=user_id, org_id=org_id, role="member"),
        session=test_session,
        limit=10,
    )

    assert response.total_count == 1
    recommendation = response.recommendations[0]
    assert recommendation.topic == "LLM evaluation framework"
    assert recommendation.recommendation_type == "capture_opportunity"
    assert recommendation.intent.intent_stage == "evaluation"
    assert recommendation.intent.target_page_type == "developer_guide"
    assert recommendation.movement.baseline_position == 18.0
    assert recommendation.movement.current_position == 11.0
    assert recommendation.movement.position_delta == 7.0
    assert recommendation.movement.click_delta == 15


def test_seed_brief_from_search_recommendation_creates_draft_payload(test_session, test_user):
    user_id, org_id = test_user
    now = datetime.now(timezone.utc)

    test_session.add(
        SearchInsight(
            organization_id=org_id,
            user_id=user_id,
            topic="Agent debugging tutorial",
            source_item_ids="1",
            our_gsc_position=None,
            our_gsc_clicks=None,
            trends_momentum="rising",
            insight_text="Search demand rising for practical debugging content.",
            generated_at=now,
        )
    )
    test_session.commit()

    recommendations_response = get_search_recommendations(
        auth=AuthContext(user_id=user_id, org_id=org_id, role="member"),
        session=test_session,
        limit=10,
    )
    recommendation = recommendations_response.recommendations[0]

    seed = seed_brief_from_search_recommendation(
        recommendation_id=recommendation.recommendation_id,
        auth=AuthContext(user_id=user_id, org_id=org_id, role="member"),
        session=test_session,
    )

    assert seed.status == "draft"
    assert seed.content_type == "blog"
    assert recommendation.topic in seed.title
    assert "## Objective" in seed.brief_md
    assert seed.metadata_json["source"] == "search_intelligence_recommendation"
    assert seed.metadata_json["seo_recommendation"]["recommendation_id"] == recommendation.recommendation_id


@pytest.mark.parametrize("recommendation_id", ["missing-id", "insight-999-cluster-0"])
def test_seed_brief_from_search_recommendation_404_when_missing(test_session, test_user, recommendation_id):
    user_id, org_id = test_user
    with pytest.raises(HTTPException) as exc:
        seed_brief_from_search_recommendation(
            recommendation_id=recommendation_id,
            auth=AuthContext(user_id=user_id, org_id=org_id, role="member"),
            session=test_session,
        )
    assert exc.value.status_code == 404
