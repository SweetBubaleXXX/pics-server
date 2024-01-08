from dependency_injector.wiring import inject, Provide
from passlib.context import CryptContext

from .models import User, UserCreate, UserRead
from ..db.dependency import DBSession
from ..containers import Container


class UsersService:
    @inject
    def __init__(
        self,
        database: DBSession,
        passlib_context: CryptContext = Provide[Container.passlib_context],
    ) -> None:
        self._db = database
        self._passlib_context = passlib_context

    def create_url(self, user: UserCreate) -> UserRead:
        hashed_password = self._passlib_context.hash(user.password)
        db_user = User(
            **user.model_dump(exclude=("password",)),
            password=hashed_password,
        )
        self._db.add(db_user)
        self._db.commit()
        self._db.refresh(db_user)
        return db_user
