from pathlib import Path
from pydantic import ConfigDict
from pydantic_settings import BaseSettings
from cryptography.fernet import Fernet
import os

class Settings(BaseSettings):
    # Repo root is 3 levels up from apps/api/ (apps/api -> apps -> repo_root)
    REPO_ROOT: Path = Path(__file__).parent.parent.parent
    
    # Personal mode flag: 'personal' (default) or 'multi_tenant'
    # In personal mode, auth is bypassed and all features are enabled
    FORGEOS_MODE: str = "personal"
    
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

    # Rate limiting (slowapi)
    RATE_LIMIT_ENABLED: bool = True
    # If behind a trusted proxy/load balancer, enable to derive client IP from X-Forwarded-For.
    RATE_LIMIT_TRUST_X_FORWARDED_FOR: bool = False
    # Storage backend for slowapi/limits (default: in-memory). Examples: "memory://", "redis://localhost:6379".
    RATE_LIMIT_STORAGE_URI: str = "memory://"

    # Per-endpoint-category limits
    RATE_LIMIT_AUTH: str = "10/minute"        # signup/signin/signout (brute-force protection)
    RATE_LIMIT_PUBLIC: str = "60/minute"      # health/legal/status (unauthenticated)
    RATE_LIMIT_INTERNAL: str = "100/minute"   # authenticated endpoints (per-user)

    # Extra global caps for expensive endpoints (applied in addition to per-user limits)
    RATE_LIMIT_EXPENSIVE_GLOBAL: str = "30/minute"

    # Logging
    LOG_LEVEL: str = "INFO"
    # Request/audit log retention (days) for rotated log files
    LOG_RETENTION_DAYS: int = 14
    # Directory to write api.log* files into
    LOG_DIR: Path = Path(__file__).parent / "logs"

    # Celery/Redis configuration
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    
    # Observability & Monitoring (P4.2)
    SENTRY_DSN: str = ""
    SENTRY_ENVIRONMENT: str = "development"
    SENTRY_TRACES_SAMPLE_RATE: float = 0.1  # 10% performance sampling
    SENTRY_PROFILE_SAMPLE_RATE: float = 0.1
    
    # Redis for caching (P4.1 optional)
    REDIS_URL: str = "redis://localhost:6379/1"
    CACHE_ENABLED: bool = True
    CACHE_TTL_SECONDS: int = 3600

    model_config = ConfigDict(env_file=".env")
    
    def __init__(self, **data):
        super().__init__(**data)
        import logging
        import base64
        logger = logging.getLogger(__name__)

        _encryption_key_from_env = os.environ.get("ENCRYPTION_KEY", "")
        _llm_key_from_env = os.environ.get("LLM_KEY_ENCRYPTION_SECRET", "")
        _jwt_key_from_env = os.environ.get("JWT_SECRET_KEY", "")

        if not self.ENCRYPTION_KEY:
            self.ENCRYPTION_KEY = Fernet.generate_key().decode()
            logger.warning("ENCRYPTION_KEY not set — using ephemeral random value. All encrypted data will be unreadable after restart.")

        if not self.LLM_KEY_ENCRYPTION_SECRET:
            self.LLM_KEY_ENCRYPTION_SECRET = base64.b64encode(os.urandom(32)).decode()
            logger.warning("LLM_KEY_ENCRYPTION_SECRET not set — using ephemeral random value.")

        if not self.JWT_SECRET_KEY:
            self.JWT_SECRET_KEY = base64.b64encode(os.urandom(32)).decode()
            logger.warning("JWT_SECRET_KEY not set — using ephemeral random value. All sessions will be invalidated on restart.")

        self._encryption_key_from_env = _encryption_key_from_env
        self._llm_key_from_env = _llm_key_from_env
        self._jwt_key_from_env = _jwt_key_from_env
        self.validate_for_production()

    def validate_for_production(self):
        if self.FORGEOS_MODE == "multi_tenant":
            missing = [k for k, v in [
                ("ENCRYPTION_KEY", self._encryption_key_from_env),
                ("LLM_KEY_ENCRYPTION_SECRET", self._llm_key_from_env),
                ("JWT_SECRET_KEY", self._jwt_key_from_env),
            ] if not v]
            if missing:
                raise RuntimeError(
                    f"FORGEOS_MODE=multi_tenant but required secrets are not set: {', '.join(missing)}. "
                    "Set these in your .env file before starting in multi-tenant mode."
                )

settings = Settings()
