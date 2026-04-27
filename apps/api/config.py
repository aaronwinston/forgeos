from pathlib import Path
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Repo root is 3 levels up from apps/api/ (apps/api -> apps -> repo_root)
    REPO_ROOT: Path = Path(__file__).parent.parent.parent
    ANTHROPIC_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    LLM_PROVIDER: str = "anthropic"
    MODEL_GENERATION: str = "claude-opus-4-7"
    MODEL_SCORING: str = "claude-haiku-4-5"
    DATABASE_URL: str = "sqlite:///./forgeos.db"

    # Canonical markdown directories (relative to REPO_ROOT)
    SKILLS_DIR: str = "skills"
    PLAYBOOKS_DIR: str = "playbooks"
    CONTEXT_DIR: str = "context"
    CORE_DIR: str = "core"
    BRIEFS_DIR: str = "briefs"
    RUBRICS_DIR: str = "rubrics"
    PROMPTS_DIR: str = "prompts"

    # Google Calendar integration
    GOOGLE_OAUTH_CLIENT_ID: str = ""
    GOOGLE_OAUTH_CLIENT_SECRET: str = ""
    GOOGLE_OAUTH_REDIRECT_URI: str = "http://localhost:8000/api/integrations/google/callback"

    class Config:
        env_file = ".env"

settings = Settings()
