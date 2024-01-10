import os
from abc import ABCMeta, abstractmethod

import aiofiles
from fastapi import Response, UploadFile
from fastapi.responses import FileResponse

from .exceptions import ImageNotFound
from .models import ImageFile

_CHUNK_SIZE = 1048576


class ImageStorage(metaclass=ABCMeta):
    @abstractmethod
    async def save_image(self, image_id: str, uploaded_file: UploadFile) -> ImageFile:
        ...

    @abstractmethod
    async def load_image(self, file_metadata: ImageFile) -> Response:
        ...

    def extract_file_metadata(self, image_id: str, file: UploadFile) -> ImageFile:
        return ImageFile(
            image_id=image_id,
            filename=file.filename,
            content_type=file.content_type,
            size=file.size,
        )


class LocalImageStorage(ImageStorage):
    def __init__(self, storage_location: str) -> None:
        self.storage_location = storage_location

    async def save_image(self, image_id: str, uploaded_file: UploadFile) -> ImageFile:
        file_metadata = self.extract_file_metadata(image_id, uploaded_file)
        image_path = self._get_image_path(image_id)
        async with aiofiles.open(image_path, "wb") as local_file:
            while chunk := await uploaded_file.read(_CHUNK_SIZE):
                await local_file.write(chunk)
        return file_metadata

    async def load_image(self, file_metadata: ImageFile) -> Response:
        image_path = self._get_image_path(str(file_metadata.image_id))
        if not os.path.exists(image_path):
            raise ImageNotFound()
        return FileResponse(
            image_path,
            media_type=file_metadata.content_type,
            filename=file_metadata.filename,
        )

    def _get_image_path(self, image_id: str) -> str:
        return os.path.join(self.storage_location, image_id)
