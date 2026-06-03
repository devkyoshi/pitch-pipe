from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Anthropic
    ANTHROPIC_API_KEY: str = ""

    # Google Cloud / Veo 3
    GOOGLE_PROJECT_ID: str = ""
    GOOGLE_REGION: str = "us-central1"
    GOOGLE_APPLICATION_CREDENTIALS: str = "/app/service_account.json"
    GCS_BUCKET_NAME: str = ""

    # LinkedIn
    LINKEDIN_ACCESS_TOKEN: str = ""
    LINKEDIN_AUTHOR_URN: str = ""

    # Meta (Instagram + Ads)
    META_ACCESS_TOKEN: str = ""
    META_IG_USER_ID: str = ""
    META_AD_ACCOUNT_ID: str = ""
    META_CAMPAIGN_ID: str = ""
    META_ADSET_ID: str = ""

    # Slack
    SLACK_WEBHOOK_URL: str = ""

    # Celery / Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Postgres
    DATABASE_URL: str = "postgresql+asyncpg://user:pass@localhost:5432/veo_pipeline"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
