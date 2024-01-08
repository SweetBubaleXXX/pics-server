from typing import Annotated, Callable

from dependency_injector.wiring import Provide, inject
from fastapi import Depends, HTTPException, Security, status
from fastapi_jwt import JwtAuthorizationCredentials
from fastapi_jwt.jwt import JwtAccess, JwtRefresh

from ..containers import Container
from ..users.exceptions import InvalidPassword, UserNotFound
from ..users.models import Role, UserRead
from ..users.service import UsersService
from .models import JwtTokenPair, LoginSchema, TokenSubject


@inject
def validate_access_token(
    token_payload: JwtAuthorizationCredentials = Security(
        Provide[Container.access_token_backend]
    ),
) -> TokenSubject:
    return TokenSubject.model_validate(token_payload.subject)


def get_user(
    credentials: Annotated[TokenSubject, Depends(validate_access_token)],
    users_service: Annotated[UsersService, Depends()],
) -> UserRead:
    user = users_service.get_user_by_id(credentials.user_id)
    if user.disabled:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "User is disabled")
    return user


def role_required(*required_roles: Role) -> Callable:
    def validate_user(user: Annotated[UserRead, Depends(get_user)]):
        if user.role not in required_roles:
            raise HTTPException(status.HTTP_403_FORBIDDEN)

    return validate_user


@inject
def authenticate_user(
    user: UserRead,
    access_token_backend: JwtAccess = Provide[Container.access_token_backend],
    refresh_token_backend: JwtRefresh = Provide[Container.refresh_token_backend],
) -> JwtTokenPair:
    token_subject = TokenSubject(user_id=user.id, role=user.role)
    serialized_subject = token_subject.model_dump()
    token_pair = JwtTokenPair(
        access_token=access_token_backend.create_access_token(serialized_subject),
        refresh_token=refresh_token_backend.create_refresh_token(serialized_subject),
    )
    return token_pair


@inject
def refresh_token(
    users_service: Annotated[UsersService, Depends()],
    token_payload: JwtAuthorizationCredentials = Security(
        Provide[Container.refresh_token_backend]
    ),
) -> JwtTokenPair:
    subject = TokenSubject.model_validate(token_payload.subject)
    user = get_user(subject, users_service)
    return authenticate_user(user)


def login_user(
    login_form: LoginSchema,
    users_service: Annotated[UsersService, Depends()],
) -> JwtTokenPair:
    try:
        user = users_service.get_user_by_credentials(
            login_form.username,
            login_form.password,
        )
    except (UserNotFound, InvalidPassword) as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST) from exc
    return authenticate_user(user)


AuthenticationRequired = Annotated[TokenSubject, Depends(validate_access_token)]
