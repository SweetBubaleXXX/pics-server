import secrets

from pydantic import Field, AnyUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        secrets_dir="/run/secrets",
        env_file=(".env", ".env.prod"),
        extra="ignore",
    )

    secret_key: str = Field(default_factory=secrets.token_hex)
    access_token_expire_minutes: int = 20

    db_url: AnyUrl
