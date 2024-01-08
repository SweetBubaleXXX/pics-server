from dependency_injector import providers
from dependency_injector.containers import DeclarativeContainer, WiringConfiguration
from passlib.context import CryptContext

from .config import Settings
from .db.service import Database


class Container(DeclarativeContainer):
    wiring_config = WiringConfiguration(
        packages=[
            ".db",
            ".users",
        ],
    )

    settings = providers.Singleton(Settings)

    passlib_context = providers.Object(CryptContext(schemes=["bcrypt"]))

    db_pool_type = providers.Object(None)
    db = providers.Singleton(
        Database,
        db_url=settings.provided.db_url,
        pool_type=db_pool_type,
    )
