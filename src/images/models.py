from datetime import datetime
from typing import Annotated, Optional
from uuid import UUID, uuid4

from pydantic import AfterValidator
from pydantic_extra_types.color import Color
from sqlmodel import Field, Relationship, SQLModel, text

from ..users.models import User, UserImageLikes

ColorField = Annotated[str, AfterValidator(lambda color: Color(color).as_hex())]


class Image(SQLModel, table=True):
    id: UUID | None = Field(default_factory=uuid4, primary_key=True)
    owner_id: int | None = Field(foreign_key="user.id")
    title: str
    description: str | None = Field(default=None)
    created_at: datetime = Field(
        sa_column_kwargs={
            "server_default": text("CURRENT_TIMESTAMP"),
        }
    )

    owner: Optional[User] = Relationship(back_populates="own_images")
    liked_by: list[User] = Relationship(
        back_populates="liked_images", link_model=UserImageLikes
    )
    file: Optional["ImageFile"] = Relationship(
        back_populates="image",
        sa_relationship_kwargs={
            "uselist": False,
            "cascade": "all,delete,delete-orphan",
        },
    )


class ImageFile(SQLModel, table=True):
    image_id: UUID | None = Field(
        default=None,
        primary_key=True,
        foreign_key="image.id",
    )
    filename: str
    content_type: str
    size: int
    width: int | None = Field(default=None)
    height: int | None = Field(default=None)
    dominant_color: str | None = None
    average_color: str | None = None

    image: Image | None = Relationship(back_populates="file")
    palette: list["ImagePaletteColor"] = Relationship(
        back_populates="file",
        sa_relationship_kwargs={"cascade": "all,delete,delete-orphan"},
    )


class ImagePaletteColor(SQLModel, table=True):
    image_id: UUID | None = Field(
        default=None,
        primary_key=True,
        foreign_key="imagefile.image_id",
    )
    color: str = Field(primary_key=True)

    file: ImageFile | None = Relationship(back_populates="palette")
