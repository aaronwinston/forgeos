import pytest
from datetime import datetime, timedelta, timezone

from models import KeywordCluster, ScrapeItem, SearchInsight
from middleware.auth import AuthContext
from routers.intelligence import _build_planning_queue, get_planning_queue


@pytest.mark.unit
def test_build_planning_queue_combines_score_recency_and_strategic_fit():
    now = datetime.now(timezone.utc)
    items = [
        ScrapeItem(
            id=1,
            organization_id="test-org-1",
            source="GitHub",
            source_url="https://example.com/1",
            title="Agent tracing patterns",
            body="Great fit for ai observability and llm evaluation",
            score=7.0,
            created_at=now - timedelta(days=1),
        ),
        ScrapeItem(
            id=2,
            organization_id="test-org-1",
            source="Reddit",
            source_url="https://example.com/2",
            title="Interesting thread",
            score=9.0,
            created_at=now - timedelta(days=12),
        ),
    ]

    queue = _build_planning_queue(
        items=items,
        keyword_terms=["ai observability"],
        rising_topics=["llm evaluation"],
    )

    assert len(queue) == 2
    assert queue[0].item_id == 1  # stronger strategic fit + recency should beat older high score
    assert queue[0].strategic_fit_signal > queue[1].strategic_fit_signal
    assert queue[0].recency_signal > queue[1].recency_signal
    assert queue[0].linkage.suggested_playbook.startswith("playbooks/")


@pytest.mark.integration
def test_get_planning_queue_returns_ranked_items(test_session, test_user):
    user_id, org_id = test_user
    now = datetime.now(timezone.utc)

    test_session.add(
        KeywordCluster(
            organization_id=org_id,
            user_id=user_id,
            keyword="ai observability",
            region="US",
            active=True,
        )
    )
    test_session.add(
        SearchInsight(
            organization_id=org_id,
            user_id=user_id,
            topic="llm evaluation",
            source_item_ids="1,2",
            trends_momentum="rising",
            insight_text="Demand is rising for evaluation content.",
        )
    )

    test_session.add_all(
        [
            ScrapeItem(
                organization_id=org_id,
                source="GitHub",
                source_url="https://example.com/alpha",
                title="AI observability for LLM evaluation",
                body="Hands-on guide",
                score=7.0,
                created_at=now - timedelta(days=1),
            ),
            ScrapeItem(
                organization_id=org_id,
                source="HackerNews",
                source_url="https://example.com/beta",
                title="General AI news",
                body="No specific keyword match",
                score=9.0,
                created_at=now - timedelta(days=20),
            ),
        ]
    )
    test_session.commit()

    data = get_planning_queue(
        auth=AuthContext(user_id=user_id, org_id=org_id, role="member"),
        session=test_session,
        limit=5,
    )

    assert len(data) == 2
    assert data[0].rank_score >= data[1].rank_score
    assert data[0].linkage.suggested_lifecycle_state in {"draft", "active"}
    assert data[0].linkage.owner_placeholder == "unassigned-content-owner"


@pytest.mark.integration
def test_get_planning_queue_empty_state(test_session, test_user):
    user_id, org_id = test_user
    data = get_planning_queue(
        auth=AuthContext(user_id=user_id, org_id=org_id, role="member"),
        session=test_session,
        limit=20,
    )
    assert data == []
