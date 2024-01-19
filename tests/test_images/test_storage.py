import os
import uuid

import pytest
from fastapi import UploadFile
from fastapi.responses import FileResponse

from src.images.exceptions import ImageNotFound
from src.images.models import ImageFile
from src.images.storage import ImageStorage

TEST_IMAGE_FILENAME = "colors.jpg"
TEST_IMAGE_MIME = "image/jpeg"


@pytest.fixture(scope="session")
def original_image_path(assets_directory: str):
    return os.path.join(assets_directory, TEST_IMAGE_FILENAME)


@pytest.fixture
def uploaded_file(original_image_path: str):
    file_size = os.stat(original_image_path).st_size
    with open(original_image_path, "rb") as image_file:
        yield UploadFile(
            image_file,
            size=file_size,
            filename=TEST_IMAGE_FILENAME,
            headers={"content-type": TEST_IMAGE_MIME},
        )


@pytest.mark.asyncio
async def test_save_image_metadata(
    image_storage: ImageStorage,
    uploaded_file: UploadFile,
):
    image_id = str(uuid.uuid4())
    file_metadata = await image_storage.save_image(image_id, uploaded_file)
    assert file_metadata.image_id == image_id
    assert file_metadata.filename == TEST_IMAGE_FILENAME
    assert file_metadata.content_type == TEST_IMAGE_MIME


@pytest.mark.asyncio
async def test_save_image_file_created(
    image_storage_location: str,
    original_image_path: str,
    image_storage: ImageStorage,
    uploaded_file: UploadFile,
):
    image_id = str(uuid.uuid4())
    await image_storage.save_image(image_id, uploaded_file)
    saved_image_path = os.path.join(image_storage_location, image_id)
    assert os.path.exists(saved_image_path)
    assert os.stat(saved_image_path).st_size == os.stat(original_image_path).st_size


@pytest.mark.asyncio
async def test_load_image_response(
    image_storage_location: str,
    image_storage: ImageStorage,
    uploaded_file: UploadFile,
):
    image_id = str(uuid.uuid4())
    image_path = os.path.join(image_storage_location, image_id)
    with open(image_path, "wb") as image_file:
        image_file.write(await uploaded_file.read())
    metadata = ImageFile(
        image_id=image_id,
        filename=uploaded_file.filename,
        content_type=uploaded_file.content_type,
    )
    response = await image_storage.load_image(metadata)
    assert isinstance(response, FileResponse)
    assert response.media_type == TEST_IMAGE_MIME
    assert response.filename == TEST_IMAGE_FILENAME


@pytest.mark.asyncio
async def test_load_image_not_found(image_storage: ImageStorage):
    metadata = ImageFile(image_id=uuid.uuid4())
    with pytest.raises(ImageNotFound):
        await image_storage.load_image(metadata)


@pytest.mark.asyncio
async def test_delete_image_not_found(image_storage: ImageStorage):
    metadata = ImageFile(image_id=uuid.uuid4())
    with pytest.raises(ImageNotFound):
        await image_storage.delete_image(metadata)
