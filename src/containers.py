from datetime import timedelta

from dependency_injector import providers
from dependency_injector.containers import DeclarativeContainer, WiringConfiguration
from fastapi_jwt import JwtAccessBearer, JwtRefreshBearerCookie
from passlib.context import CryptContext

from .config import Settings
from .db.service import Database


class Container(DeclarativeContainer):
    wiring_config = WiringConfiguration(
        packages=[
            ".auth",
            ".db",
            ".users",
        ],
    )

    settings = providers.Singleton(Settings)

    db_pool_type = providers.Object(None)
    db = providers.Singleton(
        Database,
        db_url=settings.provided.db_url,
        pool_type=db_pool_type,
    )

    passlib_context = providers.Object(CryptContext(schemes=["bcrypt"]))

    access_token_backend = providers.Singleton(
        JwtAccessBearer,
        secret_key=settings.provided.secret_key,
        access_expires_delta=timedelta(minutes=30),
        refresh_expires_delta=timedelta(days=7),
    )
    refresh_token_backend = providers.Singleton(
        JwtRefreshBearerCookie.from_other,
        access_token_backend.provided,
    )
