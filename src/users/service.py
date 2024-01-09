from functools import wraps
from typing import Callable, ParamSpec, TypeVar

from dependency_injector.wiring import Provide, inject
from fastapi import Depends
from passlib.context import CryptContext
from sqlalchemy.exc import NoResultFound
from sqlmodel import select
from sqlmodel.sql.expression import SelectOfScalar

from ..containers import Container
from ..db.session import DBSession
from .exceptions import InvalidPassword, UserAlreadyExists, UserNotFound
from .models import User, UserCreate, UserRead, UserUpdate

T = TypeVar("T")
P = ParamSpec("P")


def raises_user_not_found(func: Callable[P, T]) -> Callable[P, T]:
    @wraps(func)
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

    def get_users_raw(self) -> SelectOfScalar[User]:
        return select(User).order_by(User.username)

    def create_user(self, user: UserCreate) -> UserRead:
        existing_user = self._session.exec(
            select(User).where(User.username == user.username)
        ).first()
        if existing_user:
            raise UserAlreadyExists()
        hashed_password = self._passlib_context.hash(user.password)
        user_for_save = User(
            **user.model_dump(exclude=("password",)),
            password=hashed_password,
        )
        return self._save_user(user_for_save)

    @raises_user_not_found
    def update_user(self, user_id: int, user: UserUpdate) -> UserRead:
        user_in_db = self._session.exec(select(User).where(User.id == user_id)).one()
        user_updates = user.model_dump(exclude_unset=True)
        for field, value in user_updates.items():
            setattr(user_in_db, field, value)
        return self._save_user(user_in_db)

    @raises_user_not_found
    def delete_user(self, user_id: int) -> None:
        user = self._session.exec(select(User).where(User.id == user_id)).one()
        self._session.delete(user)
        self._session.commit()

    def _save_user(self, user: User) -> UserRead:
        self._session.add(user)
        self._session.commit()
        self._session.refresh(user)
        return UserRead.model_validate(user)
