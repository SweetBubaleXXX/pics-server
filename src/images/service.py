from abc import ABCMeta, abstractmethod
from uuid import UUID

from fastapi import Response, UploadFile


class ImageStorage(metaclass=ABCMeta):
    @abstractmethod
    async def save_image(self, image_id: UUID, file: UploadFile) -> None:
        ...

    @abstractmethod
    async def load_image(self, image_id: UUID) -> Response:
        ...


class LocalImageStorage(ImageStorage):
    pass
