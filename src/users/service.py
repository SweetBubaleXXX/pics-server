from dependency_injector.wiring import Provide, inject
from fastapi import Depends
from passlib.context import CryptContext
from sqlmodel import select
from sqlmodel.sql.expression import SelectOfScalar

from ..containers import Container
from ..db.exceptions import raises_on_not_found
from ..db.session import DBSession
from .exceptions import InvalidPassword, UserAlreadyExists, UserNotFound
from .models import User, UserCreate, UserUpdate


class UsersService:
    @inject
    def __init__(
        self,
        db_session: DBSession,
        passlib_context: CryptContext = Depends(Provide[Container.passlib_context]),
    ) -> None:
        self._session = db_session
        self._passlib_context = passlib_context

    @raises_on_not_found(UserNotFound)
    def get_user_by_id(self, user_id: int) -> User:
        return self._session.get_one(User, user_id)

    @raises_on_not_found(UserNotFound)
    def get_user_by_credentials(self, username: str, password: str) -> User:
        user = self._session.exec(select(User).where(User.username == username)).one()
        password_correct = self._passlib_context.verify(password, user.password)
        if not password_correct:
            raise InvalidPassword()
        return user

    def get_users_query(self) -> SelectOfScalar[User]:
        return select(User).order_by(User.username)

    def create_user(self, user: UserCreate) -> User:
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

    @raises_on_not_found(UserNotFound)
    def update_user(self, user_id: int, user: UserUpdate) -> User:
        user_in_db = self._session.get_one(User, user_id)
        user_updates = user.model_dump(exclude_unset=True)
        for field, value in user_updates.items():
            setattr(user_in_db, field, value)
        return self._save_user(user_in_db)

    @raises_on_not_found(UserNotFound)
    def delete_user(self, user_id: int) -> None:
        user = self._session.get_one(User, user_id)
        self._session.delete(user)
        self._session.commit()

    def _save_user(self, user: User) -> User:
        self._session.add(user)
        self._session.commit()
        self._session.refresh(user)
        return user
