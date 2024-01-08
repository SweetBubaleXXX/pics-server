from dependency_injector.wiring import Provide, inject
from passlib.context import CryptContext
from sqlmodel import select

from ..containers import Container
from ..db.session import DBSession
from .exceptions import UserNotFound
from .models import User, UserCreate, UserRead


class UsersService:
    @inject
    def __init__(
        self,
        database: DBSession,
        passlib_context: CryptContext = Provide[Container.passlib_context],
    ) -> None:
        self._db = database
        self._passlib_context = passlib_context

    def get_user_by_id(self, user_id: int) -> UserRead:
        user = self._db.exec(select(User).where(User.id == user_id)).first()
        if not user:
            raise UserNotFound()
        return UserRead.model_validate(user)

    def create_user(self, user: UserCreate) -> UserRead:
        hashed_password = self._passlib_context.hash(user.password)
        db_user = User(
            **user.model_dump(exclude=("password",)),
            password=hashed_password,
        )
        self._db.add(db_user)
        self._db.commit()
        self._db.refresh(db_user)
        return db_user
