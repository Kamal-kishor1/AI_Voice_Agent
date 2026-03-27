from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_env: str = Field(default="development", alias="APP_ENV")
    app_name: str = Field(default="Alex API", alias="APP_NAME")
    app_version: str = Field(default="0.1.0", alias="APP_VERSION")
    secret_key: str = Field(default="change-me", alias="SECRET_KEY")
    internal_api_key: str = Field(default="change-me", alias="INTERNAL_API_KEY")
    request_timeout_seconds: int = Field(default=30, alias="REQUEST_TIMEOUT_SECONDS")
    jwt_issuer: str = Field(default="https://api.antigravity.ai", alias="JWT_ISSUER")
    jwt_audience: str = Field(default="antigravity-client", alias="JWT_AUDIENCE")
    access_token_expire_seconds: int = Field(
        default=3600,
        alias="ACCESS_TOKEN_EXPIRE_SECONDS",
    )
    refresh_token_expire_days: int = Field(default=30, alias="REFRESH_TOKEN_EXPIRE_DAYS")
    jwt_private_key: str | None = Field(default=None, alias="JWT_PRIVATE_KEY")
    jwt_public_key: str | None = Field(default=None, alias="JWT_PUBLIC_KEY")
    supabase_jwks_url: str | None = Field(default=None, alias="SUPABASE_JWKS_URL")
    supabase_jwt_issuer: str | None = Field(default=None, alias="SUPABASE_JWT_ISSUER")
    supabase_jwt_audience: str | None = Field(default=None, alias="SUPABASE_JWT_AUDIENCE")
    vault_encryption_key: str | None = Field(default=None, alias="VAULT_ENCRYPTION_KEY")
    database_url: str = Field(
        default="postgresql+asyncpg://alex:alex@localhost:5432/alex",
        alias="DATABASE_URL",
    )
    redis_url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")
    database_echo: bool = Field(default=False, alias="DATABASE_ECHO")
    cors_origins: str = Field(
        default="http://localhost:3000",
        alias="CORS_ORIGINS",
    )
    google_client_id: str | None = Field(default=None, alias="GOOGLE_CLIENT_ID")
    google_client_secret: str | None = Field(default=None, alias="GOOGLE_CLIENT_SECRET")
    google_redirect_uri: str | None = Field(default=None, alias="GOOGLE_REDIRECT_URI")
    google_oauth_scopes: str = Field(
        default=(
            "openid,email,profile,"
            "https://www.googleapis.com/auth/gmail.send,"
            "https://www.googleapis.com/auth/gmail.readonly,"
            "https://www.googleapis.com/auth/calendar.events,"
            "https://www.googleapis.com/auth/drive.readonly,"
            "https://www.googleapis.com/auth/contacts.readonly"
        ),
        alias="GOOGLE_OAUTH_SCOPES",
    )
    ai_mode: str = Field(default="free", alias="AI_MODE")
    ollama_base_url: str = Field(
        default="http://localhost:11434",
        alias="OLLAMA_BASE_URL",
    )
    notification_retention_seconds: int = Field(
        default=604800,
        alias="NOTIFICATION_RETENTION_SECONDS",
    )
    anthropic_api_key: str | None = Field(default=None, alias="ANTHROPIC_API_KEY")
    openai_api_key: str | None = Field(default=None, alias="OPENAI_API_KEY")

    @property
    def parsed_cors_origins(self) -> list[str]:
        return [item.strip() for item in self.cors_origins.split(",") if item.strip()]

    @property
    def parsed_google_oauth_scopes(self) -> list[str]:
        return [item.strip() for item in self.google_oauth_scopes.split(",") if item.strip()]

    def sqlalchemy_sync_database_url(self) -> str:
        return self.database_url.replace("+asyncpg", "+psycopg")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
