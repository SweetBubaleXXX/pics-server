from typing import Annotated

from fastapi import APIRouter, Depends

from src.auth.models import JwtTokenPair
from src.auth.service import login_user

router = APIRouter()


@router.post("/jwt/create")
def create_jwt_token_pair(
    token_pair: Annotated[JwtTokenPair, Depends(login_user)],
) -> JwtTokenPair:
    return token_pair
