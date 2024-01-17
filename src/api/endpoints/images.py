from operator import attrgetter
from typing import Annotated, Iterable

from fastapi import APIRouter, Depends, Form, UploadFile, status
from fastapi_filter import FilterDepends
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlmodel import paginate

from src.auth.service import AuthenticationRequired, get_user
from src.db.session import DBSession
from src.images.filters import ImageFilter
from src.images.models import Image
from src.images.schemas import ImageDetailsSchema, ImageIdSchema
from src.images.service import ImagesService
from src.users.models import UserRead

from ..dependencies import validate_image_type

router = APIRouter(dependencies=[AuthenticationRequired])


def transform_image_details(images: Iterable[Image]) -> Iterable[ImageDetailsSchema]:
    return [
        ImageDetailsSchema(
            id=str(image.id),
            owner=image.owner.username,
            title=image.title,
            description=image.description,
            size=image.file.size,
            width=image.file.width,
            height=image.file.height,
            dominant_color=image.file.dominant_color,
            average_color=image.file.average_color,
            palette=map(attrgetter("color"), image.file.palette),
            created_at=image.created_at,
        )
        for image in images
    ]


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
        transformer=transform_image_details,
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
