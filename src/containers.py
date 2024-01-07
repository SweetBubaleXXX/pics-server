from dependency_injector.containers import DeclarativeContainer, WiringConfiguration
from dependency_injector import providers

from .config import Settings
from .database import Database


class Container(DeclarativeContainer):
    wiring_config = WiringConfiguration(
        modules=[
            ".database",
        ],
    )

    settings = providers.Singleton(Settings)

    db = providers.Singleton(Database, db_url=settings.provided.db_url)
