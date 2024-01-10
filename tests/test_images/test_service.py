import uuid

import pytest

from src.images.exceptions import ImageNotFound
from src.images.models import Image
from src.images.service import ImagesService


def test_get_image_info(images_service: ImagesService, image_factory):
    existing_image: Image = image_factory()
    found_image = images_service.get_image_info(existing_image.id)
    assert found_image.owner_id == existing_image.owner_id
    assert found_image.liked_by == []


def test_get_image_info_not_found(images_service: ImagesService):
    with pytest.raises(ImageNotFound):
        images_service.get_image_info(str(uuid.uuid4()))


@pytest.mark.asyncio
async def test_get_image_file_not_found(images_service: ImagesService):
    with pytest.raises(ImageNotFound):
        await images_service.get_image_file(str(uuid.uuid4()))
