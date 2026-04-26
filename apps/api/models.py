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
    deliverable_id: Optional[int] = Field(default=None, foreign_key="deliverable.id")
    project_id: int = Field(foreign_key="project.id")
    brief_md: str
    toggles_json: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

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
    fetched_at: datetime = Field(default_factory=datetime.utcnow)
    raw_json: Optional[str] = None
    score_relevance: Optional[float] = None
    score_reasoning: Optional[str] = None
    surfaced_to_user_at: Optional[datetime] = None
    dismissed_at: Optional[datetime] = None
