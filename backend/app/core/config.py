from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Application
    APP_NAME: str = "Sentinel"
    APP_VERSION: str = "0.1.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # API
    API_V1_PREFIX: str = "/api/v1"
    MAX_PAYLOAD_SIZE: int = 1024 * 1024  # 1MB default

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://sentinel_user:changeme@localhost:5432/sentinel"

    # JWT Configuration
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30  # 30 minutes default

    # CORS Configuration
    CORS_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000"
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: str = "*"
    CORS_ALLOW_HEADERS: str = "*"

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: str | List[str]) -> List[str]:
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    @field_validator("CORS_ALLOW_METHODS", mode="before")
    @classmethod
    def parse_cors_methods(cls, v: str | List[str]) -> List[str]:
        if isinstance(v, str):
            return [method.strip() for method in v.split(",")]
        return v

    @field_validator("CORS_ALLOW_HEADERS", mode="before")
    @classmethod
    def parse_cors_headers(cls, v: str | List[str]) -> List[str]:
        if isinstance(v, str):
            return [header.strip() for header in v.split(",")]
        return v


settings = Settings()
