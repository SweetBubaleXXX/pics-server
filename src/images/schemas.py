from pydantic import BaseModel


class ImageIdSchema(BaseModel):
    image_id: str
