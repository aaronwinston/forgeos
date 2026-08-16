from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from pydantic import BaseModel

from models import KeywordCluster, SearchInsight


class IntentMapping(BaseModel):
    intent_stage: str
    target_page_type: str
    cta_suggestion: str


class MovementSnapshot(BaseModel):
    baseline_position: Optional[float] = None
    current_position: Optional[float] = None
    position_delta: Optional[float] = None
    baseline_clicks: Optional[int] = None
    current_clicks: Optional[int] = None
    click_delta: Optional[int] = None


class SeoRecommendation(BaseModel):
    recommendation_id: str
    insight_id: int
    topic: str
    trends_momentum: str
    recommendation_type: str
    serp_gap_summary: str
    recommended_action: str
    priority_score: float
    matched_keyword_cluster_id: Optional[int] = None
    matched_keyword: Optional[str] = None
    intent: IntentMapping
    movement: MovementSnapshot


class BriefSeedPayload(BaseModel):
    title: str
    content_type: str
    status: str
    brief_md: str
    metadata_json: dict


@dataclass(frozen=True)
class _KeywordMatch:
    cluster_id: Optional[int]
    keyword: Optional[str]


_DISCOVERY_TERMS = {"what", "overview", "basics", "intro", "introduction", "guide"}
_EVALUATION_TERMS = {
    "how",
    "tutorial",
    "implementation",
    "example",
    "examples",
    "integration",
    "api",
    "sdk",
    "workflow",
    "evaluation",
}
_DECISION_TERMS = {
    "vs",
    "versus",
    "compare",
    "comparison",
    "alternatives",
    "pricing",
    "platform",
    "vendor",
    "buy",
    "best",
}


def _tokenize(value: str) -> set[str]:
    return {token.strip() for token in value.lower().replace("-", " ").split() if token.strip()}


def _find_best_keyword_match(insight: SearchInsight, keyword_clusters: list[KeywordCluster]) -> _KeywordMatch:
    searchable = f"{insight.topic} {insight.insight_text}".lower()
    insight_tokens = _tokenize(searchable)

    best: tuple[int, int, int, KeywordCluster] | None = None
    for cluster in keyword_clusters:
        keyword = (cluster.keyword or "").strip().lower()
        if not keyword:
            continue
        keyword_tokens = _tokenize(keyword)
        overlap = len(insight_tokens.intersection(keyword_tokens))
        direct_contains = 1 if keyword in searchable else 0
        score = (direct_contains, overlap, len(keyword_tokens))
        if best is None or score > best[:3]:
            best = (*score, cluster)

    if best is None or (best[0] == 0 and best[1] == 0):
        return _KeywordMatch(cluster_id=None, keyword=None)

    matched_cluster = best[3]
    return _KeywordMatch(cluster_id=matched_cluster.id, keyword=matched_cluster.keyword)


def _map_intent(topic: str, keyword: Optional[str], recommendation_type: str) -> IntentMapping:
    combined = f"{topic} {keyword or ''}".lower()
    tokens = _tokenize(combined)

    if tokens.intersection(_DECISION_TERMS):
        return IntentMapping(
            intent_stage="decision",
            target_page_type="comparison_page",
            cta_suggestion="Offer a hands-on evaluation plan with clear implementation steps.",
        )
    if recommendation_type == "defend_position":
        return IntentMapping(
            intent_stage="retention",
            target_page_type="content_refresh",
            cta_suggestion="Refresh examples and link to the latest production checklist.",
        )
    if tokens.intersection(_EVALUATION_TERMS):
        return IntentMapping(
            intent_stage="evaluation",
            target_page_type="developer_guide",
            cta_suggestion="Add a practical quickstart so engineers can test this workflow immediately.",
        )
    if tokens.intersection(_DISCOVERY_TERMS):
        return IntentMapping(
            intent_stage="awareness",
            target_page_type="educational_blog",
            cta_suggestion="Capture email subscribers with a concrete follow-up checklist.",
        )

    return IntentMapping(
        intent_stage="awareness",
        target_page_type="thought_leadership_blog",
        cta_suggestion="End with a practical next step tied to implementation guidance.",
    )


def _recommendation_type(insight: SearchInsight) -> str:
    position = insight.our_gsc_position
    if position is None or position > 10:
        if insight.trends_momentum == "rising":
            return "capture_opportunity"
        return "close_serp_gap"
    if insight.trends_momentum in {"falling", "steady"}:
        return "defend_position"
    return "expand_coverage"


def _movement(latest: SearchInsight, previous: Optional[SearchInsight]) -> MovementSnapshot:
    baseline_position = previous.our_gsc_position if previous else None
    baseline_clicks = previous.our_gsc_clicks if previous else None
    current_position = latest.our_gsc_position
    current_clicks = latest.our_gsc_clicks

    position_delta = None
    click_delta = None
    if baseline_position is not None and current_position is not None:
        position_delta = round(baseline_position - current_position, 3)
    if baseline_clicks is not None and current_clicks is not None:
        click_delta = current_clicks - baseline_clicks

    return MovementSnapshot(
        baseline_position=baseline_position,
        current_position=current_position,
        position_delta=position_delta,
        baseline_clicks=baseline_clicks,
        current_clicks=current_clicks,
        click_delta=click_delta,
    )


def _serp_gap_summary(insight: SearchInsight, recommendation_type: str) -> str:
    position = insight.our_gsc_position
    if recommendation_type == "capture_opportunity":
        if position is None:
            return "Rising topic with no current ranking footprint."
        return f"Rising topic but ranking is outside page one (position {position:.1f})."
    if recommendation_type == "close_serp_gap":
        if position is None:
            return "Topic has momentum but no ranking data yet."
        return f"Topic has room to improve from position {position:.1f}."
    if recommendation_type == "defend_position":
        return f"Current page ranks on page one (position {position:.1f}) but momentum is {insight.trends_momentum}."
    return "Topic is performing but can be expanded into deeper intent coverage."


def _recommended_action(recommendation_type: str, intent: IntentMapping, keyword: Optional[str]) -> str:
    keyword_fragment = keyword or "the topic"
    if recommendation_type == "capture_opportunity":
        return f"Ship a net-new {intent.target_page_type.replace('_', ' ')} targeting '{keyword_fragment}'."
    if recommendation_type == "defend_position":
        return f"Refresh existing page for '{keyword_fragment}' and strengthen internal links plus updated examples."
    if recommendation_type == "close_serp_gap":
        return f"Improve on-page structure for '{keyword_fragment}' with clearer H2 intent coverage and CTA alignment."
    return f"Expand '{keyword_fragment}' into a follow-on asset mapped to {intent.intent_stage} intent."


def _priority_score(insight: SearchInsight, has_keyword_match: bool, recommendation_type: str) -> float:
    momentum_weight = {
        "rising": 8.0,
        "steady": 5.0,
        "falling": 4.0,
        "no_data": 3.0,
    }.get(insight.trends_momentum, 3.0)

    position = insight.our_gsc_position
    if position is None:
        position_weight = 3.8
    elif position > 20:
        position_weight = 3.2
    elif position > 10:
        position_weight = 2.5
    elif position > 3:
        position_weight = 1.8
    else:
        position_weight = 1.0

    click_weight = min((insight.our_gsc_clicks or 0) / 50.0, 2.5)
    type_weight = {
        "capture_opportunity": 2.0,
        "defend_position": 1.5,
        "close_serp_gap": 1.2,
        "expand_coverage": 1.0,
    }.get(recommendation_type, 1.0)

    keyword_weight = 1.0 if has_keyword_match else 0.0
    score = momentum_weight + position_weight + click_weight + type_weight + keyword_weight
    return round(score, 3)


def build_actionable_recommendations(
    search_insights: list[SearchInsight],
    keyword_clusters: list[KeywordCluster],
    limit: int = 25,
) -> list[SeoRecommendation]:
    if not search_insights:
        return []

    insights_by_topic: dict[str, list[SearchInsight]] = {}
    for insight in search_insights:
        insights_by_topic.setdefault((insight.topic or "").strip().lower(), []).append(insight)

    recommendations: list[SeoRecommendation] = []
    for topic_key, topic_insights in insights_by_topic.items():
        if not topic_key:
            continue

        ordered = sorted(topic_insights, key=lambda i: i.generated_at, reverse=True)
        latest = ordered[0]
        previous = ordered[1] if len(ordered) > 1 else None

        keyword_match = _find_best_keyword_match(latest, keyword_clusters)
        recommendation_type = _recommendation_type(latest)
        intent = _map_intent(latest.topic, keyword_match.keyword, recommendation_type)
        movement = _movement(latest, previous)

        recommendation = SeoRecommendation(
            recommendation_id=f"insight-{latest.id}-cluster-{keyword_match.cluster_id or 0}",
            insight_id=latest.id or 0,
            topic=latest.topic,
            trends_momentum=latest.trends_momentum,
            recommendation_type=recommendation_type,
            serp_gap_summary=_serp_gap_summary(latest, recommendation_type),
            recommended_action=_recommended_action(recommendation_type, intent, keyword_match.keyword),
            priority_score=_priority_score(
                latest,
                has_keyword_match=keyword_match.cluster_id is not None,
                recommendation_type=recommendation_type,
            ),
            matched_keyword_cluster_id=keyword_match.cluster_id,
            matched_keyword=keyword_match.keyword,
            intent=intent,
            movement=movement,
        )
        recommendations.append(recommendation)

    recommendations.sort(key=lambda rec: (-rec.priority_score, rec.recommendation_id))
    return recommendations[:limit]


def build_brief_seed_from_recommendation(recommendation: SeoRecommendation) -> BriefSeedPayload:
    formatted_page_type = recommendation.intent.target_page_type.replace("_", " ")
    title = f"{recommendation.topic}: {formatted_page_type.title()}"
    brief_md = "\n".join(
        [
            f"# {title}",
            "",
            "## Objective",
            recommendation.recommended_action,
            "",
            "## Search context",
            f"- Momentum: {recommendation.trends_momentum}",
            f"- SERP gap: {recommendation.serp_gap_summary}",
            f"- Intent stage: {recommendation.intent.intent_stage}",
            (
                f"- Movement: position delta {recommendation.movement.position_delta}, "
                f"click delta {recommendation.movement.click_delta}"
            ),
            "",
            "## CTA",
            recommendation.intent.cta_suggestion,
        ]
    )

    recommendation_payload = (
        recommendation.model_dump()
        if hasattr(recommendation, "model_dump")
        else recommendation.dict()
    )

    return BriefSeedPayload(
        title=title,
        content_type="blog",
        status="draft",
        brief_md=brief_md,
        metadata_json={
            "seo_recommendation": recommendation_payload,
            "source": "search_intelligence_recommendation",
        },
    )
