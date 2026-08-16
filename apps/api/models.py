from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional
import uuid

from cryptography.fernet import Fernet
from sqlmodel import Field, SQLModel
from sqlalchemy import CheckConstraint, Index, UniqueConstraint

from config import settings


class Organization(SQLModel, table=True):
    __table_args__ = (
        UniqueConstraint("slug", name="uq_organization_slug"),
        CheckConstraint("plan IN ('free','pro','team')", name="ck_organization_plan"),
        CheckConstraint(
            "(subscription_status IN ('active','past_due','canceled')) OR subscription_status IS NULL",
            name="ck_organization_subscription_status",
        ),
    )

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    name: str
    slug: str
    plan: str = Field(default="free")

    trial_ends_at: Optional[datetime] = None
    stripe_customer_id: Optional[str] = None
    stripe_subscription_id: Optional[str] = None
    subscription_status: Optional[str] = None
    current_period_end: Optional[datetime] = None
    onboarding_completed_steps: Optional[str] = None  # JSON array

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Membership(SQLModel, table=True):
    __table_args__ = (
        UniqueConstraint("user_id", "organization_id", name="uq_membership_user_org"),
        CheckConstraint("role IN ('owner','admin','member')", name="ck_membership_role"),
        Index("idx_membership_org", "organization_id"),
        Index("idx_membership_user", "user_id"),
    )

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    user_id: str
    organization_id: str = Field(foreign_key="organization.id")
    role: str = Field(default="member")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Project(SQLModel, table=True):
    __table_args__ = (
        UniqueConstraint("organization_id", "name", name="uq_project_org_name"),
        CheckConstraint("status IN ('active','archived')", name="ck_project_status"),
        Index("idx_project_org", "organization_id"),
        Index("idx_project_org_user", "organization_id", "user_id"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    organization_id: str = Field(foreign_key="organization.id")
    user_id: str
    name: str
    description: Optional[str] = None
    status: str = Field(default="active")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Folder(SQLModel, table=True):
    __table_args__ = (
        UniqueConstraint(
            "organization_id",
            "project_id",
            "parent_folder_id",
            "name",
            name="uq_folder_org_project_parent_name",
        ),
        Index("idx_folder_org_project", "organization_id", "project_id"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    organization_id: str = Field(foreign_key="organization.id")
    project_id: int = Field(foreign_key="project.id")
    parent_folder_id: Optional[int] = Field(default=None, foreign_key="folder.id")
    name: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Deliverable(SQLModel, table=True):
    __table_args__ = (
        UniqueConstraint(
            "organization_id", "folder_id", "title", name="uq_deliverable_org_folder_title"
        ),
        CheckConstraint(
            "status IN ('draft','active','complete','archived','published')",
            name="ck_deliverable_status",
        ),
        Index("idx_deliverable_org_folder", "organization_id", "folder_id"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    organization_id: str = Field(foreign_key="organization.id")
    folder_id: int = Field(foreign_key="folder.id")
    content_type: str
    title: str
    status: str = Field(default="draft")
    body_md: Optional[str] = None
    metadata_json: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Brief(SQLModel, table=True):
    __table_args__ = (
        Index("idx_brief_org_project", "organization_id", "project_id"),
        Index("idx_brief_org_deliverable", "organization_id", "deliverable_id"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    organization_id: str = Field(foreign_key="organization.id")
    user_id: str
    project_id: int = Field(foreign_key="project.id")
    deliverable_id: Optional[int] = Field(default=None, foreign_key="deliverable.id")

    title: str
    audience: Optional[str] = None
    description: Optional[str] = None
    brief_md: Optional[str] = None

    toggles_json: Optional[str] = None
    context_layers_json: Optional[str] = None
    skills_json: Optional[str] = None
    intelligence_items_json: Optional[str] = None

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ChatSession(SQLModel, table=True):
    __table_args__ = (
        Index("idx_chatsession_org_created", "organization_id", "created_at"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    organization_id: str = Field(foreign_key="organization.id")
    project_id: Optional[int] = Field(default=None, foreign_key="project.id")
    folder_id: Optional[int] = Field(default=None, foreign_key="folder.id")
    deliverable_id: Optional[int] = Field(default=None, foreign_key="deliverable.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ChatMessage(SQLModel, table=True):
    __table_args__ = (
        CheckConstraint(
            "role IN ('user','assistant','system','tool')",
            name="ck_chatmessage_role",
        ),
        Index("idx_chatmessage_org_session", "organization_id", "session_id"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    organization_id: str = Field(foreign_key="organization.id")
    session_id: int = Field(foreign_key="chatsession.id")
    role: str
    content: str
    metadata_json: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ScrapeItem(SQLModel, table=True):
    __table_args__ = (
        UniqueConstraint("organization_id", "source_url", name="uq_scrapeitem_org_source_url"),
        Index("idx_scrape_org_score", "organization_id", "score"),
        Index("idx_scrape_org_created", "organization_id", "created_at"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    organization_id: str = Field(foreign_key="organization.id")

    source: str
    source_url: str
    title: str
    body: Optional[str] = None
    author: Optional[str] = None
    published_at: Optional[datetime] = None

    created_at: datetime = Field(default_factory=datetime.utcnow)
    fetched_at: datetime = Field(default_factory=datetime.utcnow)
    raw_json: Optional[str] = None

    score: Optional[float] = Field(default=None)
    score_relevance: Optional[float] = None
    score_reasoning: Optional[str] = None
    why_relevant: Optional[str] = None
    content_angle: Optional[str] = None

    surfaced_to_user_at: Optional[datetime] = None
    dismissed_at: Optional[datetime] = None


class BriefingFeedback(SQLModel, table=True):
    __table_args__ = (
        CheckConstraint("feedback_type IN ('thumbs_up','thumbs_down')", name="ck_briefingfeedback_type"),
        Index("idx_briefingfeedback_item", "briefing_item_id"),
        Index("idx_briefingfeedback_user_created", "user_id", "created_at"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    briefing_item_id: int = Field(foreign_key="scrapeitem.id")
    user_id: str  # No FK; users are external (Clerk)
    feedback_type: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


class PipelineRun(SQLModel, table=True):
    __table_args__ = (
        CheckConstraint(
            "status IN ('pending','active','complete','failed','cancelled')",
            name="ck_pipelinerun_status",
        ),
        CheckConstraint("progress >= 0 AND progress <= 100", name="ck_pipelinerun_progress"),
        Index("idx_pipelinerun_org_created", "organization_id", "created_at"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    organization_id: str = Field(foreign_key="organization.id")

    brief_id: int = Field(foreign_key="brief.id")
    deliverable_id: Optional[int] = Field(default=None, foreign_key="deliverable.id")

    title: str
    type: str = Field(default="blog")
    audience: Optional[str] = None
    description: Optional[str] = None

    status: str = Field(default="pending")
    current_agent: Optional[str] = None
    progress: int = Field(default=0)
    deleted: bool = Field(default=False)
    started_at: Optional[datetime] = None

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class PipelineStep(SQLModel, table=True):
    __table_args__ = (
        CheckConstraint("tokens_used >= 0 OR tokens_used IS NULL", name="ck_pipelinestep_tokens"),
        Index("idx_pipelinestep_org_run", "organization_id", "pipeline_run_id"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    organization_id: str = Field(foreign_key="organization.id")

    pipeline_run_id: int = Field(foreign_key="pipelinerun.id")
    agent_name: str
    input_text: str
    output_text: str
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    tokens_used: Optional[int] = None


class CalendarIntegration(SQLModel, table=True):
    __table_args__ = (
        UniqueConstraint("organization_id", name="uq_calendarintegration_org"),
        Index("idx_calendarintegration_org", "organization_id"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    organization_id: str = Field(foreign_key="organization.id")

    # Kept for backward compatibility (some codepaths don't set it)
    user_id: str = Field(default="system")

    access_token_encrypted: str = Field(default="")
    refresh_token_encrypted: str = Field(default="")
    expires_at: datetime
    calendar_id: str
    last_synced_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    @property
    def access_token(self) -> Optional[str]:
        if not self.access_token_encrypted:
            return None
        cipher = Fernet(settings.ENCRYPTION_KEY)
        return cipher.decrypt(self.access_token_encrypted.encode()).decode()

    @access_token.setter
    def access_token(self, value: Optional[str]):
        if not value:
            self.access_token_encrypted = ""
            return
        cipher = Fernet(settings.ENCRYPTION_KEY)
        self.access_token_encrypted = cipher.encrypt(value.encode()).decode()

    @property
    def refresh_token(self) -> Optional[str]:
        if not self.refresh_token_encrypted:
            return None
        cipher = Fernet(settings.ENCRYPTION_KEY)
        return cipher.decrypt(self.refresh_token_encrypted.encode()).decode()

    @refresh_token.setter
    def refresh_token(self, value: Optional[str]):
        if not value:
            self.refresh_token_encrypted = ""
            return
        cipher = Fernet(settings.ENCRYPTION_KEY)
        self.refresh_token_encrypted = cipher.encrypt(value.encode()).decode()

    def is_token_expired(self) -> bool:
        if not self.expires_at:
            return True
        return datetime.now(timezone.utc) >= self.expires_at

    def refresh_if_needed(self):
        from services.oauth import refresh_oauth_token_if_needed

        if not self.is_token_expired():
            return False

        try:
            new_access, new_refresh = refresh_oauth_token_if_needed(
                self.access_token,
                self.refresh_token,
                self.expires_at,
            )
            self.access_token = new_access
            self.refresh_token = new_refresh
            self.updated_at = datetime.now(timezone.utc)
            return True
        except Exception as e:
            import logging

            logger = logging.getLogger(__name__)
            logger.error(f"Token refresh failed: {str(e)}")
            return False


class DistributionIntegrationTarget(SQLModel, table=True):
    __table_args__ = (
        UniqueConstraint(
            "organization_id",
            "channel_type",
            "target_key",
            name="uq_distributionintegrationtarget_org_channel_key",
        ),
        CheckConstraint(
            "channel_type IN ('cms','analytics','crm','syndication')",
            name="ck_distributionintegrationtarget_channel",
        ),
        CheckConstraint(
            "delivery_mode IN ('manual','scheduled','webhook')",
            name="ck_distributionintegrationtarget_delivery_mode",
        ),
        Index(
            "idx_distributionintegrationtarget_org_channel",
            "organization_id",
            "channel_type",
        ),
    )

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    organization_id: str = Field(foreign_key="organization.id")
    created_by_user_id: str

    channel_type: str
    target_key: str
    display_name: str
    endpoint_url: Optional[str] = None

    delivery_mode: str = Field(default="scheduled")
    enabled: bool = Field(default=True)
    preferences_json: Optional[str] = None

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ConversionTaxonomyDefinition(SQLModel, table=True):
    __table_args__ = (
        UniqueConstraint(
            "organization_id",
            "deliverable_id",
            "event_key",
            name="uq_conversiontaxonomy_org_deliverable_event",
        ),
        Index(
            "idx_conversiontaxonomy_org_deliverable",
            "organization_id",
            "deliverable_id",
        ),
        Index("idx_conversiontaxonomy_org_content_type", "organization_id", "content_type"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    organization_id: str = Field(foreign_key="organization.id")
    deliverable_id: int = Field(foreign_key="deliverable.id")
    created_by_user_id: str

    content_type: str
    event_key: str
    funnel_stage: str
    definition: str
    primary_cta: Optional[str] = None
    success_metric: Optional[str] = None

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class DeliverableConversionOutcomeSnapshot(SQLModel, table=True):
    __table_args__ = (
        CheckConstraint(
            "(conversion_rate IS NULL) OR (conversion_rate >= 0 AND conversion_rate <= 1)",
            name="ck_deliverableconversionoutcome_rate",
        ),
        CheckConstraint(
            "(visitors IS NULL) OR visitors >= 0",
            name="ck_deliverableconversionoutcome_visitors",
        ),
        CheckConstraint(
            "(conversions IS NULL) OR conversions >= 0",
            name="ck_deliverableconversionoutcome_conversions",
        ),
        Index(
            "idx_deliverableconversionoutcome_org_deliverable",
            "organization_id",
            "deliverable_id",
        ),
        Index(
            "idx_deliverableconversionoutcome_org_recorded",
            "organization_id",
            "recorded_at",
        ),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    organization_id: str = Field(foreign_key="organization.id")
    deliverable_id: int = Field(foreign_key="deliverable.id")
    created_by_user_id: str

    period_label: str
    visitors: Optional[int] = None
    conversions: Optional[int] = None
    conversion_rate: Optional[float] = None
    observed_outcome: Optional[str] = None
    notes: Optional[str] = None

    recorded_at: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class DeliverableCTAExperiment(SQLModel, table=True):
    __table_args__ = (
        CheckConstraint(
            "status IN ('active','paused','completed')",
            name="ck_deliverablectaexperiment_status",
        ),
        CheckConstraint(
            "(conversion_rate IS NULL) OR (conversion_rate >= 0 AND conversion_rate <= 1)",
            name="ck_deliverablectaexperiment_rate",
        ),
        CheckConstraint(
            "(impressions IS NULL) OR impressions >= 0",
            name="ck_deliverablectaexperiment_impressions",
        ),
        CheckConstraint(
            "(conversions IS NULL) OR conversions >= 0",
            name="ck_deliverablectaexperiment_conversions",
        ),
        UniqueConstraint(
            "organization_id",
            "deliverable_id",
            "experiment_key",
            "variant_label",
            name="uq_deliverablectaexperiment_org_deliverable_variant",
        ),
        Index(
            "idx_deliverablectaexperiment_org_deliverable",
            "organization_id",
            "deliverable_id",
        ),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    organization_id: str = Field(foreign_key="organization.id")
    deliverable_id: int = Field(foreign_key="deliverable.id")
    created_by_user_id: str

    experiment_key: str
    variant_label: str
    hypothesis: Optional[str] = None
    observed_outcome: Optional[str] = None
    status: str = Field(default="active")
    impressions: Optional[int] = None
    conversions: Optional[int] = None
    conversion_rate: Optional[float] = None
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class CalendarEvent(SQLModel, table=True):
    __table_args__ = (
        UniqueConstraint(
            "organization_id",
            "google_event_id",
            name="uq_calendarevent_org_google_event_id",
        ),
        CheckConstraint(
            "status IN ('pending','confirmed','cancelled','active','archived')",
            name="ck_calendarevent_status",
        ),
        CheckConstraint(
            "sync_status IN ('synced','syncing','offline')",
            name="ck_calendarevent_sync_status",
        ),
        Index("idx_calendarevent_org_start", "organization_id", "start_at"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    organization_id: str = Field(foreign_key="organization.id")

    deliverable_id: Optional[int] = Field(default=None, foreign_key="deliverable.id")
    project_id: Optional[int] = Field(default=None, foreign_key="project.id")

    google_event_id: Optional[str] = Field(default=None)
    title: str
    content_type: str = Field(default="blog")
    description: Optional[str] = None
    notes: Optional[str] = None

    start_at: datetime
    end_at: Optional[datetime] = Field(default=None)
    all_day: bool = Field(default=True)

    status: str = Field(default="confirmed")
    sync_status: str = Field(default="offline")

    last_synced_at: Optional[datetime] = None
    synced_to_google_at: Optional[datetime] = None

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class CalendarSyncLog(SQLModel, table=True):
    __table_args__ = (
        CheckConstraint(
            "status IN ('success','error','pending','resolved_local','resolved_remote','skipped')",
            name="ck_calendarsynclog_status",
        ),
        Index("idx_calendarsynclog_org_created", "organization_id", "created_at"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    organization_id: str = Field(foreign_key="organization.id")

    event_id: Optional[int] = Field(default=None, foreign_key="calendarevent.id")
    operation: str
    status: str
    error_message: Optional[str] = None
    details_json: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class KeywordCluster(SQLModel, table=True):
    __table_args__ = (
        UniqueConstraint(
            "organization_id", "keyword", "region", name="uq_keywordcluster_org_keyword_region"
        ),
        Index("idx_keywordcluster_org_active", "organization_id", "active"),
        Index("idx_keywordcluster_org_keyword", "organization_id", "keyword"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    organization_id: str = Field(foreign_key="organization.id")
    user_id: str = Field(default="system")

    keyword: str
    region: str = Field(default="US")
    active: bool = Field(default=True)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class GscQuery(SQLModel, table=True):
    __table_args__ = (
        CheckConstraint("clicks >= 0", name="ck_gscquery_clicks"),
        CheckConstraint("impressions >= 0", name="ck_gscquery_impressions"),
        Index("idx_gscquery_org_fetched", "organization_id", "fetched_at"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    organization_id: str = Field(foreign_key="organization.id")
    user_id: str = Field(default="system")

    query: str
    page: str
    clicks: int
    impressions: int
    ctr: float
    position: float
    date_range_start: str
    date_range_end: str
    fetched_at: datetime = Field(default_factory=datetime.utcnow)


class TrendsData(SQLModel, table=True):
    __table_args__ = (
        Index("idx_trendsdata_org_fetched", "organization_id", "fetched_at"),
        Index("idx_trendsdata_org_keyword", "organization_id", "keyword"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    organization_id: str = Field(foreign_key="organization.id")
    user_id: str = Field(default="system")

    keyword: str
    region: str = Field(default="US")
    interest_over_time_json: Optional[str] = None
    related_queries_json: Optional[str] = None
    fetched_at: datetime = Field(default_factory=datetime.utcnow)


class SearchInsight(SQLModel, table=True):
    __table_args__ = (
        CheckConstraint(
            "trends_momentum IN ('rising','falling','steady','no_data')",
            name="ck_searchinsight_trends_momentum",
        ),
        Index("idx_searchinsight_org_generated", "organization_id", "generated_at"),
        Index("idx_searchinsight_org_momentum", "organization_id", "trends_momentum"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    organization_id: str = Field(foreign_key="organization.id")
    user_id: str = Field(default="system")

    topic: str
    source_item_ids: str
    our_gsc_position: Optional[float] = None
    our_gsc_clicks: Optional[int] = None
    trends_momentum: str = Field(default="no_data")
    insight_text: str
    generated_at: datetime = Field(default_factory=datetime.utcnow)


class RuntimeCredential(SQLModel, table=True):
    __table_args__ = (
        UniqueConstraint(
            "organization_id", "user_id", "runtime", name="uq_runtimecredential_org_user_runtime"
        ),
        CheckConstraint(
            "runtime IN ('anthropic','openai','copilot')",
            name="ck_runtimecredential_runtime",
        ),
        Index("idx_runtimecredential_org_user", "organization_id", "user_id"),
    )

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    organization_id: str = Field(foreign_key="organization.id")
    user_id: str
    runtime: str
    encrypted_api_key: str
    key_hash: str
    is_valid: bool = Field(default=False)
    last_validated_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class UsageEvent(SQLModel, table=True):
    __table_args__ = (
        CheckConstraint("tokens_input >= 0", name="ck_usageevent_tokens_input"),
        CheckConstraint("tokens_output >= 0", name="ck_usageevent_tokens_output"),
        CheckConstraint(
            "runtime IN ('anthropic','openai','copilot')",
            name="ck_usageevent_runtime",
        ),
        CheckConstraint(
            "event_type IN ('chat_message','pipeline_run','briefing_synthesis')",
            name="ck_usageevent_event_type",
        ),
        Index("idx_usageevent_org_time", "organization_id", "occurred_at"),
    )

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    organization_id: str = Field(foreign_key="organization.id")
    user_id: str
    event_type: str
    tokens_input: int = Field(default=0)
    tokens_output: int = Field(default=0)
    runtime: str
    cost_usd_estimate: Optional[float] = None
    occurred_at: datetime = Field(default_factory=datetime.utcnow)


class ContentEvalRun(SQLModel, table=True):
    __table_args__ = (
        CheckConstraint(
            "workflow_type IN ('blog','launch','analyst')",
            name="ck_contentevalrun_workflow_type",
        ),
        CheckConstraint("gate_status IN ('pass','fail')", name="ck_contentevalrun_gate_status"),
        Index(
            "idx_contentevalrun_org_workflow_artifact_created",
            "organization_id",
            "workflow_type",
            "artifact_key",
            "created_at",
        ),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    organization_id: str = Field(foreign_key="organization.id")
    created_by_user_id: str

    workflow_type: str
    artifact_key: str = Field(default="adhoc")
    artifact_text: str
    prompt_version: Optional[str] = None
    skill_version: Optional[str] = None

    scores_json: str
    overall_score: float
    gate_status: str
    failed_dimensions_json: Optional[str] = None

    baseline_run_id: Optional[int] = None
    deltas_json: Optional[str] = None
    regression_failed: bool = Field(default=False)
    is_baseline: bool = Field(default=False)

    created_at: datetime = Field(default_factory=datetime.utcnow)


class FeatureFlag(SQLModel, table=True):
    __table_args__ = (
        UniqueConstraint("organization_id", "flag_name", name="uq_featureflag_org_flag"),
    )

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    organization_id: str = Field(foreign_key="organization.id")
    flag_name: str
    enabled: bool = Field(default=False)
    expires_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class AuditLog(SQLModel, table=True):
    __table_args__ = (
        CheckConstraint(
            "operation IN ('CREATE','UPDATE','DELETE')",
            name="ck_auditlog_operation",
        ),
        Index("idx_auditlog_org_time", "organization_id", "created_at"),
        Index("idx_auditlog_table_record", "table_name", "record_id", "created_at"),
        Index("idx_auditlog_user_time", "user_id", "created_at"),
    )

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    organization_id: str = Field(foreign_key="organization.id")
    user_id: Optional[str] = None

    operation: str
    table_name: str
    record_id: Optional[str] = None

    old_values_json: Optional[str] = None
    new_values_json: Optional[str] = None

    request_method: Optional[str] = None
    request_path: Optional[str] = None

    created_at: datetime = Field(default_factory=datetime.utcnow)


class AuditEvent(SQLModel, table=True):
    __table_args__ = (
        CheckConstraint(
            "resource_type IN ('runtime_credential','subscription','user_data')",
            name="ck_auditevent_resource_type",
        ),
        Index("idx_auditevent_org_time", "organization_id", "created_at"),
        Index("idx_auditevent_action", "action", "created_at"),
    )

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    organization_id: str = Field(foreign_key="organization.id")
    user_id: str
    action: str
    resource_type: str
    resource_id: Optional[str] = None
    details_json: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class DoctrineVersion(SQLModel, table=True):
    __table_args__ = (
        Index(
            "idx_doctrine_org_path_time",
            "organization_id",
            "file_path",
            "created_at",
        ),
        Index("idx_doctrine_org_time", "organization_id", "created_at"),
    )

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    organization_id: str = Field(foreign_key="organization.id")
    file_path: str
    content_hash: str
    content: str
    saved_by_user_id: str
    locked_by_user_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
