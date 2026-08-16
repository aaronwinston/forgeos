"""Platform-agnostic publishing contract and adapters."""

from __future__ import annotations

import json
import re
import unicodedata
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from models import Deliverable


class ApprovalState(BaseModel):
    requires_claims_review: bool = False
    requires_technical_review: bool = False
    claims_review_approved: bool = False
    technical_review_approved: bool = False
    can_publish: bool = True
    blocking_reasons: List[str] = Field(default_factory=list)


class PublishPayload(BaseModel):
    title: str
    slug: str
    excerpt: str
    body: str
    tags: List[str] = Field(default_factory=list)
    canonical_url: Optional[str] = None
    schema_metadata: Dict[str, Any] = Field(default_factory=dict)
    cta_blocks: List[Dict[str, Any]] = Field(default_factory=list)
    approval: ApprovalState


class PublishBundle(BaseModel):
    platform: str
    deliverable_id: int
    payload: PublishPayload
    adapter_payload: Dict[str, Any]


class PublishAdapter(ABC):
    platform: str

    @abstractmethod
    def build_payload(self, payload: PublishPayload) -> Dict[str, Any]:
        raise NotImplementedError


class WordPressPublishAdapter(PublishAdapter):
    platform = "wordpress"

    def build_payload(self, payload: PublishPayload) -> Dict[str, Any]:
        return {
            "title": payload.title,
            "slug": payload.slug,
            "excerpt": payload.excerpt,
            "content": payload.body,
            "tags": payload.tags,
            "meta": {
                "canonical_url": payload.canonical_url,
                "schema_metadata": payload.schema_metadata,
                "cta_blocks": payload.cta_blocks,
                "approval": payload.approval.dict(),
            },
            "status": "draft" if not payload.approval.can_publish else "pending",
        }


def _slugify(text: str, fallback: str) -> str:
    normalized = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", normalized).strip("-").lower()
    slug = re.sub(r"-{2,}", "-", slug)
    return slug or fallback


def _normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def _normalize_tags(tags: Any) -> List[str]:
    if isinstance(tags, str):
        tags = [t.strip() for t in tags.split(",")]
    if not isinstance(tags, list):
        return []

    deduped: Dict[str, str] = {}
    for tag in tags:
        if not isinstance(tag, str):
            continue
        cleaned = _normalize_text(tag).lower()
        if cleaned:
            deduped[cleaned] = cleaned
    return sorted(deduped.values())


def _normalize_json(value: Any) -> Any:
    if isinstance(value, dict):
        return {k: _normalize_json(value[k]) for k in sorted(value.keys())}
    if isinstance(value, list):
        return [_normalize_json(v) for v in value]
    if isinstance(value, str):
        return _normalize_text(value)
    return value


def _make_excerpt(body: str, max_length: int = 220) -> str:
    cleaned = _normalize_text(body)
    if len(cleaned) <= max_length:
        return cleaned
    return cleaned[: max_length - 3].rstrip() + "..."


def _parse_metadata(metadata_json: Optional[str]) -> Dict[str, Any]:
    if not metadata_json:
        return {}
    parsed = json.loads(metadata_json)
    if not isinstance(parsed, dict):
        return {}
    return parsed


def _get_approval_state(metadata: Dict[str, Any]) -> ApprovalState:
    approval_block = metadata.get("approval", {})
    if not isinstance(approval_block, dict):
        approval_block = {}

    requires_claims_review = bool(
        metadata.get("requires_claims_review", approval_block.get("requires_claims_review", False))
    )
    requires_technical_review = bool(
        metadata.get("requires_technical_review", approval_block.get("requires_technical_review", False))
    )
    claims_review_approved = bool(
        metadata.get("claims_review_approved", approval_block.get("claims_review_approved", False))
    )
    technical_review_approved = bool(
        metadata.get("technical_review_approved", approval_block.get("technical_review_approved", False))
    )

    blocking_reasons: List[str] = []
    if requires_claims_review and not claims_review_approved:
        blocking_reasons.append("claims_review_pending")
    if requires_technical_review and not technical_review_approved:
        blocking_reasons.append("technical_review_pending")

    return ApprovalState(
        requires_claims_review=requires_claims_review,
        requires_technical_review=requires_technical_review,
        claims_review_approved=claims_review_approved,
        technical_review_approved=technical_review_approved,
        can_publish=len(blocking_reasons) == 0,
        blocking_reasons=blocking_reasons,
    )


def build_publish_payload(deliverable: Deliverable) -> PublishPayload:
    metadata = _parse_metadata(deliverable.metadata_json)
    title = _normalize_text(deliverable.title)
    fallback_slug = f"deliverable-{deliverable.id or 'untitled'}"

    body = deliverable.body_md or ""
    tags = _normalize_tags(metadata.get("tags", []))
    schema_metadata = _normalize_json(metadata.get("schema_metadata", {}))
    cta_blocks = _normalize_json(metadata.get("cta_blocks", []))
    canonical_url = metadata.get("canonical_url")
    if isinstance(canonical_url, str):
        canonical_url = canonical_url.strip() or None
    else:
        canonical_url = None

    configured_slug = metadata.get("slug")
    slug_source = configured_slug if isinstance(configured_slug, str) else title
    slug = _slugify(slug_source, fallback=fallback_slug)

    configured_excerpt = metadata.get("excerpt")
    excerpt_source = configured_excerpt if isinstance(configured_excerpt, str) else body
    excerpt = _make_excerpt(excerpt_source)

    approval = _get_approval_state(metadata)
    return PublishPayload(
        title=title,
        slug=slug,
        excerpt=excerpt,
        body=body,
        tags=tags,
        canonical_url=canonical_url,
        schema_metadata=schema_metadata if isinstance(schema_metadata, dict) else {},
        cta_blocks=cta_blocks if isinstance(cta_blocks, list) else [],
        approval=approval,
    )


ADAPTERS: Dict[str, PublishAdapter] = {
    "wordpress": WordPressPublishAdapter(),
}


def build_publish_bundle(deliverable: Deliverable, platform: str) -> PublishBundle:
    if platform not in ADAPTERS:
        raise ValueError(f"Unsupported publishing platform: {platform}")

    payload = build_publish_payload(deliverable)
    adapter_payload = ADAPTERS[platform].build_payload(payload)
    return PublishBundle(
        platform=platform,
        deliverable_id=deliverable.id or 0,
        payload=payload,
        adapter_payload=adapter_payload,
    )
