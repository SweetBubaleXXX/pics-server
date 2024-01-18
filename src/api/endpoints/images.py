from typing import Annotated

from fastapi import APIRouter, Depends, Form, UploadFile, status
from fastapi_filter import FilterDepends
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlmodel import paginate

from src.auth.service import AuthenticationRequired, get_user
from src.db.session import DBSession
from src.images.filters import ImageFilter
from src.images.models import Image
from src.images.schemas import ImageDetailsSchema, ImageIdSchema, ImageUpdateSchema
from src.images.service import ImagesService
from src.users.models import UserRead

from ..dependencies import validate_image_type

router = APIRouter(dependencies=[AuthenticationRequired])


@router.get(
    "/",
    response_model=Page[ImageDetailsSchema],
)
async def list_images(
    db_session: DBSession,
    image_filter: Annotated[ImageFilter, FilterDepends(ImageFilter)],
    images_service: Annotated[ImagesService, Depends()],
):
    query = images_service.filter_images_query(image_filter)
    return paginate(
        db_session,
        query,
        transformer=lambda images: list(map(ImageDetailsSchema.from_model, images)),
    )


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(validate_image_type)],
)
async def upload_image(
    owner: Annotated[UserRead, Depends(get_user)],
    images_service: Annotated[ImagesService, Depends()],
    file: UploadFile,
    title: Annotated[str, Form()],
    description: str | None = Form(default=None),
) -> ImageIdSchema:
    image_details = Image(owner_id=owner.id, title=title, description=description)
    image = await images_service.create_image(image_details, file)
    return ImageIdSchema(image_id=str(image.id))


@router.patch("/{image_id}/")
def update_image_info(
    image_id: str,
    images_service: Annotated[ImagesService, Depends()],
    image_update: ImageUpdateSchema,
) -> ImageDetailsSchema:
    updated_image = images_service.update_image_details(image_id, image_update)
    return ImageDetailsSchema.from_model(updated_image)


@router.post("/{image_id}/upload", dependencies=[Depends(validate_image_type)])
async def change_image(
    image_id: str,
    images_service: Annotated[ImagesService, Depends()],
    file: UploadFile,
) -> ImageIdSchema:
    await images_service.update_image_file(image_id, file)
    return ImageIdSchema(image_id=image_id)
