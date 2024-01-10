from pydantic import BaseModel

from ..users.models import Role


class TokenSubject(BaseModel):
    user_id: int
    role: Role


class JwtTokenPair(BaseModel):
    access_token: str
    refresh_token: str
