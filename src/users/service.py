from typing import Callable, ParamSpec, TypeVar

from dependency_injector.wiring import Provide, inject
from fastapi import Depends
from passlib.context import CryptContext
from sqlalchemy.exc import NoResultFound
from sqlmodel import select

from ..containers import Container
from ..db.session import DBSession
from .exceptions import InvalidPassword, UserNotFound
from .models import User, UserCreate, UserRead

T = TypeVar("T")
P = ParamSpec("P")


def raises_user_not_found(func: Callable[P, T]) -> Callable[P, T]:
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        try:
            return func(*args, **kwargs)
        except NoResultFound as exc:
            raise UserNotFound() from exc

    return wrapper


class UsersService:
    @inject
    def __init__(
        self,
        db_session: DBSession,
        passlib_context: CryptContext = Depends(Provide[Container.passlib_context]),
    ) -> None:
        self._session = db_session
        self._passlib_context = passlib_context

    @raises_user_not_found
    def get_user_by_id(self, user_id: int) -> UserRead:
        user = self._session.exec(select(User).where(User.id == user_id)).one()
        return UserRead.model_validate(user)

    @raises_user_not_found
    def get_user_by_credentials(self, username: str, password: str) -> UserRead:
        user = self._session.exec(select(User).where(User.username == username)).one()
        password_correct = self._passlib_context.verify(password, user.password)
        if not password_correct:
            raise InvalidPassword()
        return UserRead.model_validate(user)

    def create_user(self, user: UserCreate) -> UserRead:
        hashed_password = self._passlib_context.hash(user.password)
        db_user = User(
            **user.model_dump(exclude=("password",)),
            password=hashed_password,
        )
        self._session.add(db_user)
        self._session.commit()
        self._session.refresh(db_user)
        return UserRead.model_validate(db_user)
