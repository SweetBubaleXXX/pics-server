from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlmodel import paginate

from src.auth.models import RegistrationSchema
from src.auth.service import role_required
from src.db.session import DBSession
from src.users.models import Role, UserCreate, UserRead, UserUpdate
from src.users.service import UsersService

router = APIRouter()


@router.get(
    "/",
    response_model=Page[UserRead],
    dependencies=[Depends(role_required(Role.EMPLOYEE, Role.ADMIN))],
)
def get_users(
    db_session: DBSession,
    users_service: Annotated[UsersService, Depends()],
):
    raw_query = users_service.get_users_raw()
    return paginate(db_session, raw_query)


@router.post("/")
def create_user(
    credentials: RegistrationSchema,
    users_service: Annotated[UsersService, Depends()],
) -> UserRead:
    user = UserCreate.model_validate(credentials)
    return users_service.create_user(user)


@router.get(
    "/{user_id}",
    dependencies=[Depends(role_required(Role.EMPLOYEE, Role.ADMIN))],
)
def read_user(
    user_id: int,
    users_service: Annotated[UsersService, Depends()],
) -> UserRead:
    return users_service.get_user_by_id(user_id)


@router.patch(
    "/{user_id}",
    dependencies=[Depends(role_required(Role.ADMIN))],
)
def update_user(
    user_id: int,
    user_update: UserUpdate,
    users_service: Annotated[UsersService, Depends()],
) -> UserRead:
    return users_service.update_user(user_id, user_update)


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(role_required(Role.ADMIN))],
)
def delete_user(
    user_id: int,
    users_service: Annotated[UsersService, Depends()],
):
    users_service.delete_user(user_id)
