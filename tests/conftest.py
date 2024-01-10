import pytest
import pytest_asyncio
from asgi_lifespan import LifespanManager
from factory import Faker
from factory.alchemy import SQLAlchemyModelFactory
from fastapi import FastAPI
from sqlalchemy import StaticPool
from sqlmodel import Session

from src.config import Settings
from src.containers import Container
from src.db.service import Database
from src.db.session import get_db_session
from src.main import create_app
from src.users.models import User
from src.users.service import UsersService

TEST_DB_URL = "sqlite:///:memory:"


@pytest.fixture(scope="session")
def assets_directory():
    return "tests/assets"


@pytest.fixture(scope="session")
def app():
    return create_app()


@pytest.fixture(scope="session")
def container(app: FastAPI):
    return app.container


@pytest.fixture(scope="session", autouse=True)
def override_settings(container: Container):
    container.settings.override(Settings(db_url=TEST_DB_URL))
    yield
    container.settings.reset_override()


@pytest.fixture(scope="session", autouse=True)
def override_db_pool(container: Container):
    container.db_pool_type.override(StaticPool)
    yield
    container.db_pool_type.reset_override()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def trigger_lifespan_events(app: FastAPI):
    async with LifespanManager(app):
        yield


@pytest.fixture
def database(container: Container):
    return container.db()


@pytest.fixture
def db_session(database: Database):
    return database.session()


@pytest.fixture(autouse=True)
def override_db_session(app: FastAPI, db_session: Session):
    app.dependency_overrides[get_db_session] = lambda: db_session


@pytest.fixture
def user_factory(db_session: Session):
    class UserFactory(SQLAlchemyModelFactory):
        username = Faker("name")
        password = Faker("password")

        class Meta:
            model = User
            sqlalchemy_session = db_session
            sqlalchemy_session_persistence = "flush"

    return UserFactory


@pytest.fixture
def users_service(db_session: Session):
    return UsersService(db_session)
