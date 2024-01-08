from sqlmodel import Session, select

from src.users.models import User, UserCreate
from src.users.service import UsersService


def test_create_user_hashed_password(
    db_session: Session,
    users_service: UsersService,
    user_factory,
):
    user = UserCreate.model_validate(user_factory())
    created_user = users_service.create_url(user)
    user_in_db = db_session.exec(select(User).where(User.id == created_user.id)).first()
    assert user_in_db.password != user.password
