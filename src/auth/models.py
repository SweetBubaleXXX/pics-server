from pydantic import BaseModel


class JwtTokenPair(BaseModel):
    access_token: str
    refresh_token: str


class JwtTokenPayload(BaseModel):
    user_id: int
