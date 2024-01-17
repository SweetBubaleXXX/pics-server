import secrets
from datetime import timedelta
from pathlib import Path

from fastapi_jwt import JwtAccessBearer, JwtRefreshBearerCookie
from pydantic import AnyUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class _SettingsModelConfigMixin:
    model_config = SettingsConfigDict(
        secrets_dir="/run/secrets",
        env_file=(".env", ".env.prod"),
        extra="ignore",
    )


class SecretKeySettings(_SettingsModelConfigMixin, BaseSettings):
    secret_key: str = Field(default_factory=secrets.token_hex)


class Settings(_SettingsModelConfigMixin, BaseSettings):
    db_url: AnyUrl

    image_storage_location: Path | AnyUrl = ".images/"
    image_palette_color_count: int = 5


SECRET_KEY = SecretKeySettings().secret_key


access_token_backend = JwtAccessBearer(
    secret_key=SECRET_KEY,
    access_expires_delta=timedelta(minutes=30),
    refresh_expires_delta=timedelta(days=7),
)
refresh_token_backend = JwtRefreshBearerCookie.from_other(
    access_token_backend,
)
