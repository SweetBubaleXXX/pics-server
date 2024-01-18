from typing import Annotated

from fastapi import Depends, HTTPException, UploadFile, status

from src.auth.service import get_user
from src.images.constants import ALLOWED_IMAGE_MIME_TYPES
from src.images.models import Image
from src.images.service import ImagesService
from src.users.models import UserRead


def validate_image_type(file: UploadFile) -> None:
    if file.content_type not in ALLOWED_IMAGE_MIME_TYPES:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid image format")


def get_image_by_id(
    image_id: str,
    images_service: Annotated[ImagesService, Depends()],
) -> Image:
    return images_service.get_image_details(image_id)


def is_own_image(
    user: Annotated[UserRead, Depends(get_user)],
    image: Annotated[Image, Depends(get_image_by_id)],
) -> None:
    if image.owner_id != user.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN)
