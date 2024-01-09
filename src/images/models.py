from datetime import datetime
from typing import TYPE_CHECKING, Optional
from uuid import UUID, uuid4

from pydantic_extra_types.color import Color
from sqlmodel import AutoString, Column, Field, Relationship, SQLModel, text

if TYPE_CHECKING:
    from ..users.models import User


class ImageLikes(SQLModel, table=True):
    user_id: int | None = Field(default=None, foreign_key="user.id", primary_key=True)
    image_id: UUID | None = Field(
        default=None,
        foreign_key="image.id",
        primary_key=True,
    )


class Image(SQLModel, table=True):
    id: UUID | None = Field(default_factory=uuid4, primary_key=True)
    owner_id: int | None = Field(foreign_key="user.id")
    title: str
    filename: str
    uploaded_at: datetime = Field(
        sa_column_kwargs={
            "server_default": text("CURRENT_TIMESTAMP"),
        }
    )

    owner: Optional["User"] = Relationship(back_populates="own_images")
    details: Optional["ImageDetails"] = Relationship(
        back_populates="image",
        sa_relationship_kwargs={"uselist": False},
    )
    palette: list["ImagePaletteColor"] = Relationship(back_populates="image")
    liked_by: list["User"] = Relationship(
        back_populates="liked_images", link_model=ImageLikes
    )


class ImageDetails(SQLModel, table=True):
    image_id: UUID | None = Field(
        default=None,
        primary_key=True,
        foreign_key="image.id",
    )
    size: int
    description: str | None = Field(default=None)
    width: int | None = Field(default=None)
    height: int | None = Field(default=None)
    dominant_color: Color | None = Field(default=None, sa_column=Column(AutoString()))
    average_color: Color | None = Field(default=None, sa_column=Column(AutoString()))

    image: Image | None = Relationship(back_populates="details")


class ImagePaletteColor(SQLModel, table=True):
    image_id: UUID | None = Field(
        default=None,
        foreign_key="image.id",
        primary_key=True,
    )
    color: Color = Field(sa_column=Column(AutoString()))

    image: Image | None = Relationship(back_populates="palette")
