from datetime import datetime

from pydantic import BaseModel


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
