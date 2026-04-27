from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field
from cryptography.fernet import Fernet
from config import settings

class Project(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(default="aaron")
    name: str
    description: Optional[str] = None
    status: str = Field(default="active")
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Folder(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    project_id: int = Field(foreign_key="project.id")
    parent_folder_id: Optional[int] = Field(default=None, foreign_key="folder.id")
    name: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Deliverable(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
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
    user_id: str = Field(default="aaron")
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
    project_id: Optional[int] = Field(default=None, foreign_key="project.id")
    folder_id: Optional[int] = Field(default=None, foreign_key="folder.id")
    deliverable_id: Optional[int] = Field(default=None, foreign_key="deliverable.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ChatMessage(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: int = Field(foreign_key="chatsession.id")
    role: str
    content: str
    metadata_json: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ScrapeItem(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
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
    pipeline_run_id: int = Field(foreign_key="pipelinerun.id")
    agent_name: str
    input_text: str
    output_text: str
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    tokens_used: Optional[int] = None

class CalendarIntegration(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(default="aaron")
    _access_token: str = Field(alias="_access_token")  # encrypted in DB
    _refresh_token: str = Field(alias="_refresh_token")  # encrypted in DB
    expires_at: datetime
    calendar_id: str
    last_synced_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    @property
    def access_token(self) -> str:
        """Decrypt access token on read."""
        if not self._access_token:
            return None
        cipher = Fernet(settings.ENCRYPTION_KEY)
        return cipher.decrypt(self._access_token.encode()).decode()

    @access_token.setter
    def access_token(self, value: str):
        """Encrypt access token on write."""
        if not value:
            self._access_token = None
            return
        cipher = Fernet(settings.ENCRYPTION_KEY)
        self._access_token = cipher.encrypt(value.encode()).decode()

    @property
    def refresh_token(self) -> str:
        """Decrypt refresh token on read."""
        if not self._refresh_token:
            return None
        cipher = Fernet(settings.ENCRYPTION_KEY)
        return cipher.decrypt(self._refresh_token.encode()).decode()

    @refresh_token.setter
    def refresh_token(self, value: str):
        """Encrypt refresh token on write."""
        if not value:
            self._refresh_token = None
            return
        cipher = Fernet(settings.ENCRYPTION_KEY)
        self._refresh_token = cipher.encrypt(value.encode()).decode()

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

class TrendsData(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(default="aaron")
    keyword: str
    region: str = Field(default="US")
    interest_over_time_json: Optional[str] = None
    related_queries_json: Optional[str] = None
    fetched_at: datetime = Field(default_factory=datetime.utcnow)

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
