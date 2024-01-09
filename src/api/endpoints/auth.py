from typing import Annotated

from fastapi import APIRouter, Depends, Response

from src.auth import service
from src.auth.models import JwtTokenPair

router = APIRouter()


@router.post("/jwt/create")
def create_jwt_token_pair(
    token_pair: Annotated[JwtTokenPair, Depends(service.authenticate_user)],
) -> JwtTokenPair:
    return token_pair


@router.post("/jwt/refresh")
def refresh_token(
    token_pair: Annotated[JwtTokenPair, Depends(service.refresh_token)],
) -> JwtTokenPair:
    return token_pair


@router.post(
    "/jwt/logout",
    dependencies=(service.AuthenticationRequired,),
)
def logout(response: Response) -> None:
    service.logout(response)
