from typing import Annotated

from fastapi import APIRouter, Depends

from src.auth.models import RegistrationSchema
from src.users.models import UserRead, UserUpdate
from src.users.service import UsersService

router = APIRouter()


@router.post("/")
def create_user(
    credentials: RegistrationSchema,
    users_service: Annotated[UsersService, Depends()],
) -> UserRead:
    user = UserUpdate.model_validate(credentials)
    return users_service.create_user(user)
