from pydantic import BaseModel, Field

from ..users.models import PASSWORD_CONSTRAINTS, USERNAME_CONSTRAINTS, Role


class TokenSubject(BaseModel):
    user_id: int
    role: Role


class JwtTokenPair(BaseModel):
    access_token: str
    refresh_token: str


class LoginSchema(BaseModel):
    username: str = Field(**USERNAME_CONSTRAINTS, pattern=r"^\w+$")
    password: str = Field(**PASSWORD_CONSTRAINTS)


class RegistrationSchema(LoginSchema):
    pass
