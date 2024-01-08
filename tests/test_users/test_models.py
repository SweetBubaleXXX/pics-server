from src.users.models import Role


def test_default_role(user_factory):
    user = user_factory()
    assert user.role is Role.USER
