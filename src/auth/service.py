from typing import Annotated, Callable

from fastapi import Depends, HTTPException, Response, Security, status
from fastapi_jwt import JwtAuthorizationCredentials

from ..config import access_token_backend, refresh_token_backend
from ..users.exceptions import InvalidPassword, UserNotFound
from ..users.models import Role, User
from ..users.service import UsersService
from .models import JwtTokenPair, TokenSubject
from .schemas import LoginSchema


def validate_access_token(
    token_payload: JwtAuthorizationCredentials = Security(access_token_backend),
) -> TokenSubject:
    return TokenSubject.model_validate(token_payload.subject)


def get_user(
    credentials: Annotated[TokenSubject, Depends(validate_access_token)],
    users_service: Annotated[UsersService, Depends()],
) -> User:
    user = users_service.get_user_by_id(credentials.user_id)
    if user.disabled:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "User is disabled")
    return user


def role_required(*required_roles: Role) -> Callable:
    def validate_user(user: Annotated[User, Depends(get_user)]):
        if user.role not in required_roles:
            raise HTTPException(status.HTTP_403_FORBIDDEN)

    return validate_user


def issue_tokens(
    response: Response,
    user: User,
) -> Response:
    token_subject = TokenSubject(user_id=user.id, role=user.role)
    serialized_subject = token_subject.model_dump()
    token_pair = JwtTokenPair(
        access_token=access_token_backend.create_access_token(serialized_subject),
        refresh_token=refresh_token_backend.create_refresh_token(serialized_subject),
    )
    refresh_token_backend.set_refresh_cookie(
        response,
        token_pair.refresh_token,
        refresh_token_backend.refresh_expires_delta,
    )
    return token_pair


def refresh_token(
    response: Response,
    users_service: Annotated[UsersService, Depends()],
    token_payload: JwtAuthorizationCredentials = Security(refresh_token_backend),
) -> JwtTokenPair:
    subject = TokenSubject.model_validate(token_payload.subject)
    user = get_user(subject, users_service)
    return issue_tokens(response, user)


def authenticate_user(
    response: Response,
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
    return issue_tokens(response, user)


def logout(response: Response) -> None:
    refresh_token_backend.unset_refresh_cookie(response)


AuthenticationRequired = Depends(validate_access_token)
