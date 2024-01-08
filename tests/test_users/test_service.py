import pytest
from factory import Factory
from sqlmodel import Session, select

from src.users.exceptions import UserNotFound
from src.users.models import User, UserCreate
from src.users.service import UsersService


def test_get_user_by_id_not_found(users_service: UsersService):
    with pytest.raises(UserNotFound):
        users_service.get_user_by_id(123)


def test_get_user_by_id(user_factory: Factory, users_service: UsersService):
    user: User = user_factory()
    found_user = users_service.get_user_by_id(user.id)
    assert found_user.username == user.username


def test_get_user_by_credentials(user_factory: Factory, users_service: UsersService):
    user = UserCreate.model_validate(user_factory.build())
    saved_used = users_service.create_user(user)
    found_user = users_service.get_user_by_credentials(user.username, user.password)
    assert found_user.id == saved_used.id


def test_create_user_hashed_password(
    db_session: Session,
    users_service: UsersService,
    user_factory: Factory,
):
    user = UserCreate.model_validate(user_factory.build())
    created_user = users_service.create_user(user)
    user_in_db = db_session.exec(select(User).where(User.id == created_user.id)).first()
    assert user_in_db.password != user.password
