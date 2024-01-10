from typing import Annotated

from fastapi import APIRouter, Depends, Form, UploadFile, status

from src.auth.service import AuthenticationRequired, get_user
from src.images.models import Image
from src.images.schemas import ImageIdSchema
from src.images.service import ImagesService
from src.users.models import UserRead

router = APIRouter(dependencies=[AuthenticationRequired])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def upload_image(
    owner: Annotated[UserRead, Depends(get_user)],
    images_service: Annotated[ImagesService, Depends()],
    file: UploadFile,
    title: Annotated[str, Form()],
    description: str | None = Form(default=None),
) -> ImageIdSchema:
    image_details = Image(owner_id=owner.id, title=title, description=description)
    image = await images_service.create_image(image_details, file)
    return ImageIdSchema(image_id=image.id)
