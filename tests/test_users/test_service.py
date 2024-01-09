import pytest
from factory import Factory
from sqlmodel import Session, select

from src.users import exceptions
from src.users.models import User, UserCreate, UserRead, UserUpdate
from src.users.service import UsersService


def test_get_user_by_id(user_factory: Factory, users_service: UsersService):
    user: User = user_factory()
    found_user = users_service.get_user_by_id(user.id)
    assert found_user.username == user.username
    assert isinstance(found_user, UserRead)


def test_get_user_by_id_not_found(users_service: UsersService):
    with pytest.raises(exceptions.UserNotFound):
        users_service.get_user_by_id(123)


def test_get_user_by_credentials(user_factory: Factory, users_service: UsersService):
    user = UserCreate.model_validate(user_factory.build())
    saved_used = users_service.create_user(user)
    found_user = users_service.get_user_by_credentials(user.username, user.password)
    assert found_user.id == saved_used.id


def test_get_user_by_credentials_not_found(users_service: UsersService):
    with pytest.raises(exceptions.UserNotFound):
        users_service.get_user_by_credentials("username", "password")


def test_create_user_already_exists(
    user_factory: Factory,
    users_service: UsersService,
):
    existing_user: User = user_factory()
    user_for_creation = UserCreate.model_validate(existing_user)
    with pytest.raises(exceptions.UserAlreadyExists):
        users_service.create_user(user_for_creation)


def test_create_user_hashed_password(
    db_session: Session,
    user_factory: Factory,
    users_service: UsersService,
):
    user = UserCreate.model_validate(user_factory.build())
    created_user = users_service.create_user(user)
    user_in_db = db_session.exec(select(User).where(User.id == created_user.id)).one()
    assert user_in_db.password != user.password


def test_update_user(
    db_session: Session,
    user_factory: Factory,
    users_service: UsersService,
):
    existing_user: User = user_factory()
    previous_value = existing_user.disabled
    user_update = UserUpdate(disabled=not previous_value)
    users_service.update_user(existing_user.id, user_update)
    user_in_db = db_session.exec(select(User).where(User.id == existing_user.id)).one()
    assert user_in_db.disabled != previous_value


def test_update_user_not_found(users_service: UsersService):
    with pytest.raises(exceptions.UserNotFound):
        users_service.update_user(123, UserUpdate())


def test_delete_user(
    db_session: Session,
    user_factory: Factory,
    users_service: UsersService,
):
    existing_user: User = user_factory()
    users_service.delete_user(existing_user.id)
    user_in_db = db_session.exec(
        select(User).where(User.id == existing_user.id)
    ).first()
    assert not user_in_db


def test_delete_user_not_found(users_service: UsersService):
    with pytest.raises(exceptions.UserNotFound):
        users_service.delete_user(123)
