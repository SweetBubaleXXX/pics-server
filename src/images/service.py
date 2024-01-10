from colorthief import ColorThief
from dependency_injector.wiring import Provide, inject
from fastapi import BackgroundTasks, Depends, Response, UploadFile

from ..config import Settings
from ..containers import Container
from ..db.session import DBSession
from .models import Image, ImageFile, ImagePaletteColor
from .storage import ImageStorage


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

    def get_image_info(self, image_id: str) -> Image:
        ...

    def get_image_file(self, image_id: str) -> Response:
        ...

    def create_image(self, image: Image, file: UploadFile) -> Image:
        self._session.add(image)
        self._session.commit()
        self._background_tasks.add_task(self._save_image, image, file)

    def update_image_info(self) -> ...:
        ...

    def update_image_file(self, image_id: str, file: UploadFile) -> None:
        ...

    async def _save_image(self, image: Image, file: UploadFile) -> None:
        image_metadata = await self._storage.save_image(image.id, file)
        await file.seek(0)
        self._background_tasks.add_task(self._process_image, image_metadata, file)

    def _process_image(self, image_metadata: ImageFile, file: UploadFile) -> None:
        color_thief = ColorThief(file.file)
        image_metadata.width, image_metadata.height = color_thief.image.size
        image_metadata.dominant_color = color_thief.get_color()
        palette = color_thief.get_palette(color_count=self._palette_color_count)
        for color in palette:
            image_metadata.palette.append(ImagePaletteColor(color=color))
        self._session.add(image_metadata)
        self._session.commit()
