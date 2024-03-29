from fastapi import APIRouter

from .endpoints import auth, images, users

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(images.router, prefix="/images", tags=["images"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
