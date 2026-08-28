from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # App
    PROJECT_NAME: str = "Shadow AI Sentinel"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    FRONTEND_URL: str = "http://localhost:5173"

    # Security
    SECRET_KEY: str = "shadow_ai_sentinel_super_secret_jwt_key_2026_change_in_production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours
    PASSWORD_RESET_EXPIRE_MINUTES: int = 30

    # Supabase
    SUPABASE_URL: Optional[str] = None
    # Legacy anon key (older Supabase projects)
    SUPABASE_ANON_KEY: Optional[str] = None
    # Publishable key (newer Supabase projects — replaces anon key, safe for server use)
    SUPABASE_PUBLISHABLE_KEY: Optional[str] = None
    # Service role key — SERVER-SIDE ONLY, bypasses RLS. Never expose to clients.
    SUPABASE_SERVICE_KEY: Optional[str] = None

    @property
    def supabase_safe_key(self) -> Optional[str]:
        """Returns the publishable key if set, falling back to the legacy anon key."""
        return self.SUPABASE_PUBLISHABLE_KEY or self.SUPABASE_ANON_KEY

    # Seed Admin User
    ADMIN_NAME: str = "Saravana Kumar M"
    ADMIN_EMAIL: str = "admin@enterprise.com"
    ADMIN_PASSWORD: str = "AdminSecure2026!"

    # Google OAuth
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/auth/google/callback"

    # Anthropic LLM API (for AI Investigator Agent)
    ANTHROPIC_API_KEY: Optional[str] = None
    ANTHROPIC_MODEL: str = "claude-sonnet-4-6"

    # SMTP / Email
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_FROM_EMAIL: str = "no-reply@shadowai-sentinel.local"
    ENABLE_EMAIL_ALERTS: bool = False

    # Slack Alerts
    SLACK_WEBHOOK_URL: Optional[str] = None
    ENABLE_SLACK_ALERTS: bool = False

    # Risk Scoring Weights (4 Signals)
    WEIGHT_CATEGORY_SENSITIVITY: float = 0.35
    WEIGHT_SANCTION_STATUS: float = 0.30
    WEIGHT_DATA_EXPOSURE: float = 0.20
    WEIGHT_USAGE_SPREAD: float = 0.15

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
