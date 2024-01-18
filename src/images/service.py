from io import IOBase
from uuid import UUID

import cv2
import numpy as np
from colorthief import ColorThief
from dependency_injector.wiring import Provide, inject
from fastapi import BackgroundTasks, Depends, Response, UploadFile
from pydantic_extra_types.color import Color
from sqlalchemy.orm import selectinload
from sqlalchemy.util import greenlet_spawn
from sqlmodel import select
from sqlmodel.sql.expression import SelectOfScalar

from src.users.models import User

from ..config import Settings
from ..containers import Container
from ..db.exceptions import raises_on_not_found
from ..db.session import DBSession, get_database
from .exceptions import ImageNotFound
from .filters import ImageFilter
from .models import Image, ImageFile, ImagePaletteColor
from .schemas import ImageUpdateSchema
from .storage import ImageStorage, copy_to_temp_file


def find_average_color(image_buffer: IOBase) -> Color:
    image_buffer.seek(0)
    content = np.frombuffer(image_buffer.read(), dtype=np.uint8)
    image = cv2.imdecode(content, cv2.IMREAD_UNCHANGED)
    average_color_per_row = np.mean(image, axis=0)
    average_color = np.mean(average_color_per_row, axis=0)
    b, g, r = average_color
    return Color((r, g, b)).as_hex()


@inject
def process_image(
    image_id: str,
    content: IOBase,
    settings: Settings = Provide[Container.settings],
) -> None:
    with get_database().session() as session:
        file_metadata = session.exec(
            select(ImageFile).where(ImageFile.image_id == image_id)
        ).one()
        color_thief = ColorThief(content)
        file_metadata.width, file_metadata.height = color_thief.image.size
        file_metadata.dominant_color = Color(color_thief.get_color()).as_hex()
        file_metadata.average_color = find_average_color(content)
        file_metadata.palette.clear()
        palette = color_thief.get_palette(
            color_count=settings.image_palette_color_count
        )
        for color in palette:
            file_metadata.palette.append(ImagePaletteColor(color=Color(color).as_hex()))
        session.add(file_metadata)
        session.commit()


class ImagesService:
    @inject
    def __init__(
        self,
        db_session: DBSession,
        background_task: BackgroundTasks,
        storage: ImageStorage = Depends(Provide[Container.image_storage]),
    ) -> None:
        self._session = db_session
        self._background_tasks = background_task
        self._storage = storage

    @raises_on_not_found(ImageNotFound)
    def get_image_details(self, image_id: str | UUID) -> Image:
        image = self._session.exec(
            select(Image)
            .where(Image.id == image_id)
            .options(selectinload("*").selectinload("*"))
        ).one()
        return image

    @raises_on_not_found(ImageNotFound)
    async def get_image_file(self, image_id: str | UUID) -> Response:
        query = select(ImageFile).where(ImageFile.image_id == image_id)
        query_result = await greenlet_spawn(self._session.exec, query)
        file_metadata = query_result.one()
        return await self._storage.load_image(file_metadata)

    def filter_images_query(self, image_filter: ImageFilter) -> SelectOfScalar[Image]:
        query = select(Image).options(selectinload("*").selectinload("*"))
        return image_filter.filter(query)

    async def create_image(self, image: Image, file: UploadFile) -> Image:
        await greenlet_spawn(self._session.add, image)
        await self._save_image_file(str(image.id), file)
        await greenlet_spawn(self._session.commit)
        await greenlet_spawn(self._session.refresh, image)
        return image

    def update_image_details(
        self,
        image: Image,
        updated_details: ImageUpdateSchema,
    ) -> Image:
        image_updates = updated_details.model_dump(exclude_unset=True)
        for field, value in image_updates.items():
            setattr(image, field, value)
        self._session.add(image)
        self._session.commit()
        self._session.refresh(image)
        return image

    @raises_on_not_found(ImageNotFound)
    async def update_image_file(self, image_id: str, file: UploadFile) -> None:
        await self._save_image_file(image_id, file)
        await greenlet_spawn(self._session.commit)

    @raises_on_not_found(ImageNotFound)
    def like_image(self, image_id: str | UUID, user_id: int) -> None:
        image = self._session.exec(select(Image).where(Image.id == image_id)).one()
        user = self._session.exec(select(User).where(User.id == user_id)).one()
        if user not in image.liked_by:
            image.liked_by.append(user)

    def delete_image(self, image: Image) -> None:
        self._session.delete(image)
        self._session.commit()

    async def _save_image_file(self, image_id: str, file: UploadFile) -> ImageFile:
        file_metadata = await self._storage.save_image(image_id, file)
        await greenlet_spawn(self._session.merge, file_metadata)
        temp_file = await copy_to_temp_file(file)
        self._background_tasks.add_task(process_image, image_id, temp_file)
        return file_metadata
