from datetime import datetime
from operator import attrgetter
from typing import Self

from pydantic import BaseModel

from .models import Image


class ImageIdSchema(BaseModel):
    image_id: str


class ImageDetailsSchema(BaseModel):
    id: str
    owner: str
    title: str
    description: str | None = None
    size: int | None
    width: int | None = None
    height: int | None = None
    dominant_color: str | None = None
    average_color: str | None = None
    palette: list[str] = []
    created_at: datetime

    @classmethod
    def from_model(cls, instance: Image) -> Self:
        return cls(
            id=str(instance.id),
            owner=instance.owner.username,
            title=instance.title,
            description=instance.description,
            size=instance.file.size,
            width=instance.file.width,
            height=instance.file.height,
            dominant_color=instance.file.dominant_color,
            average_color=instance.file.average_color,
            palette=map(attrgetter("color"), instance.file.palette),
            created_at=instance.created_at,
        )


class ImageUpdateSchema(BaseModel):
    title: str
    description: str | None = None
