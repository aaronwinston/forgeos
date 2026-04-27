from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field
from sqlalchemy import Index
from pydantic import PrivateAttr
from cryptography.fernet import Fernet
from config import settings
import uuid

class Organization(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    name: str
    slug: str
    plan: str = Field(default="free")  # free|pro|team
    trial_ends_at: Optional[datetime] = None
    stripe_customer_id: Optional[str] = None
    stripe_subscription_id: Optional[str] = None
    subscription_status: Optional[str] = None  # active|past_due|canceled
    current_period_end: Optional[datetime] = None
    onboarding_completed_steps: Optional[str] = None  # JSON array of completed step IDs
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class Membership(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    user_id: str
    organization_id: str = Field(foreign_key="organization.id")
    role: str = Field(default="member")  # owner|admin|member
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Project(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    organization_id: str = Field(foreign_key="organization.id")
    user_id: str
    name: str
    description: Optional[str] = None
    status: str = Field(default="active")
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Folder(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    organization_id: str = Field(foreign_key="organization.id")
    project_id: int = Field(foreign_key="project.id")
    parent_folder_id: Optional[int] = Field(default=None, foreign_key="folder.id")
    name: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Deliverable(SQLModel, table=True):
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
    id: Optional[int] = Field(default=None, primary_key=True)
    organization_id: str = Field(foreign_key="organization.id")
    project_id: Optional[int] = Field(default=None, foreign_key="project.id")
    folder_id: Optional[int] = Field(default=None, foreign_key="folder.id")
    deliverable_id: Optional[int] = Field(default=None, foreign_key="deliverable.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ChatMessage(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    organization_id: str = Field(foreign_key="organization.id")
    session_id: int = Field(foreign_key="chatsession.id")
    role: str
    content: str
    metadata_json: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ScrapeItem(SQLModel, table=True):
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

class PipelineRun(SQLModel, table=True):
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
    id: Optional[int] = Field(default=None, primary_key=True)
    organization_id: str = Field(foreign_key="organization.id")
    user_id: str
    access_token_encrypted: str = Field(default="")
    refresh_token_encrypted: str = Field(default="")
    expires_at: datetime
    calendar_id: str
    last_synced_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    @property
    def access_token(self) -> str:
        """Decrypt access token on read."""
        if not self.access_token_encrypted:
            return None
        cipher = Fernet(settings.ENCRYPTION_KEY)
        return cipher.decrypt(self.access_token_encrypted.encode()).decode()

    @access_token.setter
    def access_token(self, value: str):
        """Encrypt access token on write."""
        if not value:
            self.access_token_encrypted = ""
            return
        cipher = Fernet(settings.ENCRYPTION_KEY)
        self.access_token_encrypted = cipher.encrypt(value.encode()).decode()

    @property
    def refresh_token(self) -> str:
        """Decrypt refresh token on read."""
        if not self.refresh_token_encrypted:
            return None
        cipher = Fernet(settings.ENCRYPTION_KEY)
        return cipher.decrypt(self.refresh_token_encrypted.encode()).decode()

    @refresh_token.setter
    def refresh_token(self, value: str):
        """Encrypt refresh token on write."""
        if not value:
            self.refresh_token_encrypted = ""
            return
        cipher = Fernet(settings.ENCRYPTION_KEY)
        self.refresh_token_encrypted = cipher.encrypt(value.encode()).decode()
    
    def is_token_expired(self) -> bool:
        """Check if access token is expired."""
        if not self.expires_at:
            return True
        return datetime.utcnow() >= self.expires_at
    
    def refresh_if_needed(self):
        """Refresh OAuth token if expired."""
        from services.oauth import refresh_oauth_token_if_needed
        
        if not self.is_token_expired():
            return False
        
        try:
            new_access, new_refresh = refresh_oauth_token_if_needed(
                self.access_token,
                self.refresh_token,
                self.expires_at
            )
            self.access_token = new_access
            self.refresh_token = new_refresh
            self.updated_at = datetime.utcnow()
            return True
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Token refresh failed: {str(e)}")
            return False

class CalendarEvent(SQLModel, table=True):
    """
    A calendar event tied (optionally) to a Deliverable.

    status follows RFC 5545: 'pending' | 'confirmed' | 'cancelled'.
    sync_status reflects the Google Calendar round-trip state used by the UI
    to render ✓ synced / ⟳ syncing / ⚠ offline badges.
    google_event_id, last_synced_at, synced_to_google_at are managed by the
    OAuth/sync layer (Phase 3.3 Opus scope via /api/integrations).
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    # Optional — event may exist before a deliverable is created
    deliverable_id: Optional[int] = Field(default=None, foreign_key="deliverable.id")
    # For project context when no deliverable exists yet
    project_id: Optional[int] = Field(default=None, foreign_key="project.id")
    google_event_id: Optional[str] = Field(default=None)
    title: str
    # blog | email | press-release | case-study | whitepaper | launch
    content_type: str = Field(default="blog")
    description: Optional[str] = None
    notes: Optional[str] = None
    start_at: datetime
    end_at: Optional[datetime] = Field(default=None)
    all_day: bool = Field(default=True)
    # RFC 5545 event status + operational states: pending | confirmed | cancelled | archived
    status: str = Field(default="confirmed")
    # UI sync indicator managed by the OAuth sync layer: synced | syncing | offline
    sync_status: str = Field(default="offline")
    last_synced_at: Optional[datetime] = None
    synced_to_google_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class CalendarSyncLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    event_id: Optional[int] = Field(default=None, foreign_key="calendarevent.id")
    operation: str
    status: str
    error_message: Optional[str] = None
    details_json: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class KeywordCluster(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(default="aaron")
    keyword: str
    region: str = Field(default="US")
    active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_keyword_cluster_user_active', 'user_id', 'active'),
        Index('idx_keyword_cluster_keyword', 'keyword'),
    )

class GscQuery(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(default="aaron")
    query: str
    page: str
    clicks: int
    impressions: int
    ctr: float
    position: float
    date_range_start: str
    date_range_end: str
    fetched_at: datetime = Field(default_factory=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_gsc_query_user_query', 'user_id', 'query'),
        Index('idx_gsc_query_user_page', 'user_id', 'page'),
        Index('idx_gsc_query_fetched', 'user_id', 'fetched_at'),
    )

class TrendsData(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(default="aaron")
    keyword: str
    region: str = Field(default="US")
    interest_over_time_json: Optional[str] = None
    related_queries_json: Optional[str] = None
    fetched_at: datetime = Field(default_factory=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_trends_data_user_keyword', 'user_id', 'keyword'),
        Index('idx_trends_data_fetched', 'user_id', 'fetched_at'),
    )

class SearchInsight(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(default="aaron")
    topic: str
    source_item_ids: str
    our_gsc_position: Optional[float] = None
    our_gsc_clicks: Optional[int] = None
    trends_momentum: str = Field(default="no_data")
    insight_text: str
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_search_insight_user_momentum', 'user_id', 'trends_momentum'),
        Index('idx_search_insight_generated', 'user_id', 'generated_at'),
        Index('idx_search_insight_topic', 'user_id', 'topic'),
    )

class RuntimeCredential(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    organization_id: str = Field(foreign_key="organization.id")
    user_id: str
    runtime: str  # anthropic|openai|copilot
    encrypted_api_key: str
    key_hash: str
    is_valid: bool = Field(default=False)
    last_validated_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class UsageEvent(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    organization_id: str = Field(foreign_key="organization.id")
    user_id: str
    event_type: str  # chat_message|pipeline_run|briefing_synthesis
    tokens_input: int = Field(default=0)
    tokens_output: int = Field(default=0)
    runtime: str  # anthropic|openai|copilot
    cost_usd_estimate: Optional[float] = None
    occurred_at: datetime = Field(default_factory=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_usage_org_time', 'organization_id', 'occurred_at'),
        Index('idx_usage_runtime_time', 'runtime', 'occurred_at'),
    )

class FeatureFlag(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    organization_id: str = Field(foreign_key="organization.id")
    flag_name: str
    enabled: bool = Field(default=False)
    expires_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class AuditEvent(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    organization_id: str = Field(foreign_key="organization.id")
    user_id: str
    action: str  # credential_added|credential_removed|subscription_created|subscription_canceled|data_exported|data_deleted
    resource_type: str  # runtime_credential|subscription|user_data
    resource_id: Optional[str] = None
    details_json: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_audit_org_time', 'organization_id', 'created_at'),
        Index('idx_audit_action', 'action', 'created_at'),
    )

