from fastapi import HTTPException, UploadFile, status

from src.images.constants import ALLOWED_IMAGE_MIME_TYPES


def validate_image_type(file: UploadFile) -> None:
    if file.content_type not in ALLOWED_IMAGE_MIME_TYPES:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid image format")
