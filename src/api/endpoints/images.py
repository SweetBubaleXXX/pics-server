from typing import Annotated

from fastapi import APIRouter, Depends, Form, Response, UploadFile, status
from fastapi_filter import FilterDepends
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlmodel import paginate

from src.auth.service import AuthenticationRequired, get_user
from src.db.session import DBSession
from src.images.filters import ImageFilter
from src.images.models import Image
from src.images.schemas import ImageDetailsSchema, ImageIdSchema, ImageUpdateSchema
from src.images.service import ImagesService
from src.users.models import User

from ..dependencies import get_image_by_id, is_own_image, validate_image_type

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
        transformer=ImageDetailsSchema.from_model_bulk,
    )


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(validate_image_type)],
)
async def upload_image(
    owner: Annotated[User, Depends(get_user)],
    images_service: Annotated[ImagesService, Depends()],
    file: UploadFile,
    title: Annotated[str, Form()],
    description: str | None = Form(default=None),
) -> ImageIdSchema:
    image_details = Image(owner=owner, title=title, description=description)
    image = await images_service.create_image(image_details, file)
    return ImageIdSchema(image_id=str(image.id))


@router.get(
    "/liked",
    response_model=Page[ImageDetailsSchema],
)
async def list_liked_images(
    user: Annotated[User, Depends(get_user)],
    db_session: DBSession,
    image_filter: Annotated[ImageFilter, FilterDepends(ImageFilter)],
    images_service: Annotated[ImagesService, Depends()],
):
    query = images_service.get_liked_images_query(user)
    image_filter.filter(query)
    return paginate(
        db_session,
        query,
        transformer=ImageDetailsSchema.from_model_bulk,
    )


@router.post("/liked/{image_id}", status_code=status.HTTP_204_NO_CONTENT)
def like_image(
    user: Annotated[User, Depends(get_user)],
    image: Annotated[Image, Depends(get_image_by_id)],
    images_service: Annotated[ImagesService, Depends()],
):
    images_service.like_image(image, user)


@router.delete("/liked/{image_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_like(
    user: Annotated[User, Depends(get_user)],
    image: Annotated[Image, Depends(get_image_by_id)],
    images_service: Annotated[ImagesService, Depends()],
):
    images_service.remove_like(image, user)


@router.get("/{image_id}/")
async def download_image(
    image_id: str,
    images_service: Annotated[ImagesService, Depends()],
) -> Response:
    return await images_service.get_image_file(image_id)


@router.patch(
    "/{image_id}/",
    dependencies=[Depends(is_own_image)],
)
def update_image_info(
    image: Annotated[Image, Depends(get_image_by_id)],
    images_service: Annotated[ImagesService, Depends()],
    image_update: ImageUpdateSchema,
) -> ImageDetailsSchema:
    updated_image = images_service.update_image_details(image, image_update)
    return ImageDetailsSchema.from_model(updated_image)


@router.post(
    "/{image_id}/upload",
    dependencies=[Depends(validate_image_type), Depends(is_own_image)],
)
async def change_image(
    image_id: str,
    images_service: Annotated[ImagesService, Depends()],
    file: UploadFile,
) -> ImageIdSchema:
    await images_service.update_image_file(image_id, file)
    return ImageIdSchema(image_id=image_id)


@router.delete(
    "/{image_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(is_own_image)],
)
def delete_image(
    image: Annotated[Image, Depends(get_image_by_id)],
    images_service: Annotated[ImagesService, Depends()],
):
    images_service.delete_image(image)
