from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field

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
    access_token: str
    refresh_token: str
    expires_at: datetime
    calendar_id: str
    last_synced_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class CalendarEvent(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    deliverable_id: int = Field(foreign_key="deliverable.id")
    google_event_id: Optional[str] = None
    title: str
    description: Optional[str] = None
    start_at: datetime
    end_at: datetime
    status: str = Field(default="active")
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
