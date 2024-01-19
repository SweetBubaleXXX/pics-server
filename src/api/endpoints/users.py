from typing import Annotated, Any

from fastapi import APIRouter, Depends, status
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlmodel import paginate

from src.auth.schemas import RegistrationSchema
from src.auth.service import get_user, role_required
from src.db.session import DBSession
from src.users.models import Role, User, UserCreate, UserRead, UserUpdate
from src.users.service import UsersService

router = APIRouter()


@router.get("/me", response_model=UserRead)
def get_current_user(user: Annotated[User, Depends(get_user)]) -> Any:
    return user


@router.get(
    "/",
    response_model=Page[UserRead],
    dependencies=[Depends(role_required(Role.EMPLOYEE, Role.ADMIN))],
)
def list_users(
    db_session: DBSession,
    users_service: Annotated[UsersService, Depends()],
):
    query = users_service.get_users_query()
    return paginate(db_session, query)


@router.post("/", response_model=UserRead)
def create_user(
    credentials: RegistrationSchema,
    users_service: Annotated[UsersService, Depends()],
) -> Any:
    user = UserCreate.model_validate(credentials)
    return users_service.create_user(user)


@router.get(
    "/{user_id}",
    response_model=UserRead,
    dependencies=[Depends(role_required(Role.EMPLOYEE, Role.ADMIN))],
)
def read_user(
    user_id: int,
    users_service: Annotated[UsersService, Depends()],
) -> Any:
    return users_service.get_user_by_id(user_id)


@router.patch(
    "/{user_id}",
    response_model=UserRead,
    dependencies=[Depends(role_required(Role.ADMIN))],
)
def update_user(
    user_id: int,
    user_update: UserUpdate,
    users_service: Annotated[UsersService, Depends()],
) -> Any:
    return users_service.update_user(user_id, user_update)


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(role_required(Role.ADMIN))],
)
def delete_user(
    user_id: int,
    users_service: Annotated[UsersService, Depends()],
) -> None:
    users_service.delete_user(user_id)
