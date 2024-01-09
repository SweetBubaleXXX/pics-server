import secrets
from datetime import timedelta

from fastapi_jwt import JwtAccessBearer, JwtRefreshBearerCookie
from pydantic import AnyUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class _SettingsConfigMixin:
    model_config = SettingsConfigDict(
        secrets_dir="/run/secrets",
        env_file=(".env", ".env.prod"),
        extra="ignore",
    )


class SecretKeySettings(_SettingsConfigMixin, BaseSettings):
    value: str = Field(default_factory=secrets.token_hex)


class Settings(_SettingsConfigMixin, BaseSettings):
    db_url: AnyUrl


SECRET_KEY = SecretKeySettings().value


access_token_backend = JwtAccessBearer(
    secret_key=SECRET_KEY,
    access_expires_delta=timedelta(minutes=30),
    refresh_expires_delta=timedelta(days=7),
)
refresh_token_backend = JwtRefreshBearerCookie.from_other(
    access_token_backend,
)
