from pathlib import Path
from pydantic_settings import BaseSettings
from cryptography.fernet import Fernet
import os

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
    
    # Token encryption key (Fernet symmetric key)
    # Generate with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
    ENCRYPTION_KEY: str = ""
    
    # Stripe keys (M2 Billing & Metering)
    STRIPE_PUBLIC_KEY: str = ""
    STRIPE_SECRET_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""
    
    # LLM key encryption (M2)
    LLM_KEY_ENCRYPTION_SECRET: str = ""
    
    # CORS allowed origins (comma-separated list)
    CORS_ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:3001"
    
    # JWT secret key for auth tokens
    JWT_SECRET_KEY: str = ""

    class Config:
        env_file = ".env"
    
    def __init__(self, **data):
        super().__init__(**data)
        # If ENCRYPTION_KEY not provided, generate one (should warn in production)
        if not self.ENCRYPTION_KEY:
            self.ENCRYPTION_KEY = os.environ.get("ENCRYPTION_KEY", Fernet.generate_key().decode())
        
        # If LLM_KEY_ENCRYPTION_SECRET not provided, generate one
        if not self.LLM_KEY_ENCRYPTION_SECRET:
            import base64
            self.LLM_KEY_ENCRYPTION_SECRET = base64.b64encode(os.urandom(32)).decode()
        
        # If JWT_SECRET_KEY not provided, generate one
        if not self.JWT_SECRET_KEY:
            import base64
            self.JWT_SECRET_KEY = base64.b64encode(os.urandom(32)).decode()

settings = Settings()
