from dependency_injector import providers
from dependency_injector.containers import DeclarativeContainer, WiringConfiguration
from passlib.context import CryptContext

from .config import Settings
from .db.service import Database
from .images.storage import LocalImageStorage


class Container(DeclarativeContainer):
    wiring_config = WiringConfiguration(
        packages=[
            ".db",
            ".images",
            ".users",
        ],
    )

    settings = providers.Singleton(Settings)

    db_pool_type = providers.Object(None)
    db = providers.ThreadSafeSingleton(
        Database,
        db_url=settings.provided.db_url,
        pool_type=db_pool_type,
    )

    image_storage = providers.Factory(
        LocalImageStorage,
        storage_location=settings.provided.image_storage_location,
    )

    passlib_context = providers.Object(CryptContext(schemes=["bcrypt"]))
