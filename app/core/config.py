import json
from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

    APP_NAME: str = "Bhoomi Certificate Backend"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    DATABASE_URL: str = "postgresql+psycopg://postgres:postgres@localhost:5432/bhoomi_certificates"

    JWT_SECRET: str = "change_me"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_HOURS: int = 8

    ADMIN_EMAIL: str = "admin@bhoomi.local"
    ADMIN_PASSWORD: str = "change_admin_password"

    PINATA_JWT: str = ""
    PINATA_BASE_URL: str = "https://api.pinata.cloud"
    IPFS_GATEWAY_BASE_URL: str = "https://gateway.pinata.cloud/ipfs"
    POLYGON_RPC_URL: str = "https://rpc-amoy.polygon.technology"

    CORS_ORIGINS: list[str] = Field(
        default_factory=lambda: [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "https://matrix3-0-frontend-odgw.vercel.app"
        ]
    )
    CORS_ALLOW_ORIGIN_REGEX: str | None = r"^https:\/\/.*\.devtunnels\.ms$"

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def normalize_database_url(cls, value: str) -> str:
        # SQLAlchemy with psycopg v3 expects the explicit driver in URL scheme.
        if isinstance(value, str):
            if value.startswith("postgresql://"):
                return value.replace("postgresql://", "postgresql+psycopg://", 1)
            if value.startswith("postgres://"):
                return value.replace("postgres://", "postgresql+psycopg://", 1)
        return value

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def normalize_cors_origins(cls, value: list[str] | str) -> list[str]:
        if isinstance(value, str):
            raw = value.strip()
            if not raw:
                return []
            if raw.startswith("["):
                try:
                    parsed = json.loads(raw)
                    if isinstance(parsed, list):
                        return [str(item).rstrip("/") for item in parsed]
                except json.JSONDecodeError:
                    pass
            return [item.strip().rstrip("/") for item in raw.split(",") if item.strip()]

        return [str(item).rstrip("/") for item in value]

    @field_validator("CORS_ALLOW_ORIGIN_REGEX", mode="before")
    @classmethod
    def normalize_cors_origin_regex(cls, value: str | None) -> str | None:
        if value is None:
            return None

        cleaned = str(value).strip()
        if not cleaned:
            return None

        return cleaned


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
