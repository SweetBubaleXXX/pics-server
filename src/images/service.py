from io import IOBase

from colorthief import ColorThief
from dependency_injector.wiring import Provide, inject
from fastapi import BackgroundTasks, Depends, Response, UploadFile
from sqlalchemy.orm import selectinload
from sqlalchemy.util import greenlet_spawn
from sqlmodel import select

from ..config import Settings
from ..containers import Container
from ..db.exceptions import raises_on_not_found
from ..db.session import DBSession
from .exceptions import ImageNotFound
from .models import Image, ImageFile, ImagePaletteColor
from .storage import ImageStorage, copy_to_temp_file


class ImagesService:
    @inject
    def __init__(
        self,
        db_session: DBSession,
        background_task: BackgroundTasks,
        storage: ImageStorage = Depends(Provide[Container.image_storage]),
        settings: Settings = Depends(Provide[Container.settings]),
    ) -> None:
        self._session = db_session
        self._background_tasks = background_task
        self._storage = storage

        self._palette_color_count = settings.image_palette_color_count

    @raises_on_not_found(ImageNotFound)
    def get_image_details(self, image_id: str) -> Image:
        image = self._session.exec(
            select(Image)
            .where(Image.id == image_id)
            .options(selectinload("*").selectinload("*"))
        ).one()
        return image

    @raises_on_not_found(ImageNotFound)
    async def get_image_file(self, image_id: str) -> Response:
        query = select(ImageFile).where(ImageFile.image_id == image_id)
        query_result = await greenlet_spawn(self._session.exec, query)
        file_metadata = query_result.one()
        return await self._storage.load_image(file_metadata)

    async def create_image(self, image: Image, file: UploadFile) -> Image:
        await greenlet_spawn(self._session.add, image)
        await self._save_image(image, file)
        await greenlet_spawn(self._session.commit)
        await greenlet_spawn(self._session.refresh, image)
        return image

    def update_image_details(self) -> ...:
        ...

    def update_image_file(self, image_id: str, file: UploadFile) -> None:
        ...

    async def _save_image(self, image: Image, file: UploadFile) -> None:
        image_metadata = await self._storage.save_image(str(image.id), file)
        await greenlet_spawn(self._session.add, image_metadata)
        temp_file = await copy_to_temp_file(file)
        self._background_tasks.add_task(self._process_image, image_metadata, temp_file)

    def _process_image(self, image_metadata: ImageFile, content: IOBase) -> None:
        color_thief = ColorThief(content)
        image_metadata.width, image_metadata.height = color_thief.image.size
        image_metadata.dominant_color = color_thief.get_color()
        palette = color_thief.get_palette(color_count=self._palette_color_count)
        for color in palette:
            image_metadata.palette.append(ImagePaletteColor(color=color))
        self._session.add(image_metadata)
        self._session.commit()
