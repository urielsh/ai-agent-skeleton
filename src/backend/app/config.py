"""Application configuration via environment variables."""

from functools import lru_cache

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """All configuration loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Database
    database_url: str = "postgresql+asyncpg://appdev:appdev@localhost:5432/app"

    # Redis (optional — empty string disables)
    redis_url: str = "redis://localhost:6379/0"

    # LLM Provider: "anthropic" or "openai"
    llm_provider: str = "anthropic"

    # Anthropic
    anthropic_api_key: str = ""
    anthropic_chat_model: str = "claude-sonnet-4-5-20250514"

    # OpenAI
    openai_api_key: str = ""
    openai_chat_model: str = "gpt-4o"

    # Application
    cors_allowed_origins: str = ""
    llm_timeout_sec: float = 45.0
    compute_timeout_sec: float = 30.0
    chat_sla_sec: float = 3.0
    prompt_version: str = "1.0"
    reports_dir: str = "reports"

    # LLM retry on transient errors
    llm_retry_max: int = 2
    llm_retry_base_sec: float = 1.0

    # LLM sampling parameters (deterministic defaults)
    llm_temperature: float = 0.0
    llm_top_p: float = 1.0
    llm_frequency_penalty: float = 0.0

    # Redis
    redis_draft_ttl_sec: int = 86400

    # Rate limiting
    rate_limit_per_minute: int = 30

    @model_validator(mode="after")
    def validate_required_keys(self) -> "Settings":
        """Fail fast if required API key is missing for the chosen provider."""
        provider = self.llm_provider.lower()
        if provider not in ("anthropic", "openai"):
            raise ValueError(
                f"LLM_PROVIDER must be 'anthropic' or 'openai', got '{self.llm_provider}'"
            )
        if provider == "anthropic" and not self.anthropic_api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY is required when LLM_PROVIDER=anthropic"
            )
        if provider == "openai" and not self.openai_api_key:
            raise ValueError(
                "OPENAI_API_KEY is required when LLM_PROVIDER=openai"
            )
        if self.llm_retry_max < 0 or self.llm_retry_max > 5:
            raise ValueError("LLM_RETRY_MAX must be between 0 and 5")
        return self


@lru_cache
def get_settings() -> Settings:
    """Cached settings singleton."""
    return Settings()
