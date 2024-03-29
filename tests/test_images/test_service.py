import uuid

import pytest
from sqlmodel import Session, select

from src.images.exceptions import ImageNotFound
from src.images.models import Image
from src.images.schemas import ImageUpdateSchema
from src.images.service import ImagesService
from src.users.exceptions import UserNotFound
from src.users.models import User


def test_get_image_details(images_service: ImagesService, image_factory):
    existing_image: Image = image_factory()
    found_image = images_service.get_image_details(existing_image.id)
    assert found_image.owner_id == existing_image.owner_id
    assert found_image.liked_by == []


def test_get_image_details_not_found(images_service: ImagesService):
    with pytest.raises(ImageNotFound):
        images_service.get_image_details(uuid.uuid4())


@pytest.mark.asyncio
async def test_get_image_file_not_found(images_service: ImagesService):
    with pytest.raises(ImageNotFound):
        await images_service.get_image_file(str(uuid.uuid4()))


def test_update_image_details(
    db_session: Session,
    images_service: ImagesService,
    image_factory,
):
    existing_image: Image = image_factory()
    image_update = ImageUpdateSchema(title="new title", description="new description")
    images_service.update_image_details(existing_image, image_update)
    image_in_db = db_session.exec(
        select(Image).where(Image.id == existing_image.id)
    ).one()
    assert image_in_db.title == image_update.title
    assert image_in_db.description == image_update.description


def test_like_image(
    db_session: Session,
    images_service: ImagesService,
    image_factory,
    user_factory,
):
    image: Image = image_factory()
    user: User = user_factory()
    images_service.like_image(image, user)
    image_in_db = db_session.exec(select(Image).where(Image.id == image.id)).one()
    assert user in image_in_db.liked_by


def test_remove_like(
    db_session: Session,
    images_service: ImagesService,
    image_factory,
    user_factory,
):
    image: Image = image_factory()
    user: User = user_factory(liked_images=[image])
    images_service.remove_like(image, user)
    image_in_db = db_session.exec(select(Image).where(Image.id == image.id)).one()
    assert user not in image_in_db.liked_by


def test_remove_like_not_found(
    images_service: ImagesService,
    image_factory,
    user_factory,
):
    image: Image = image_factory()
    user: User = user_factory()
    with pytest.raises(UserNotFound):
        images_service.remove_like(image, user)
