from enum import StrEnum, auto

from sqlmodel import Enum, Field, Relationship, SQLModel

from ..images.models import Image, ImageLikes

USERNAME_CONSTRAINTS = dict(min_length=4, max_length=20)
PASSWORD_CONSTRAINTS = dict(min_length=8, max_length=30)


class Role(StrEnum):
    USER = auto()
    EMPLOYEE = auto()
    ADMIN = auto()


class UserBase(SQLModel):
    username: str = Field(unique=True, **USERNAME_CONSTRAINTS)
    role: Role = Field(sa_column=Enum(Role), default=Role.USER)
    disabled: bool = False


class UserRead(UserBase):
    id: int


class UserCreate(UserBase):
    password: str = Field(**PASSWORD_CONSTRAINTS)


class UserUpdate(SQLModel):
    role: Role | None = None
    disabled: bool | None = None
    password: str | None = None


class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    password: str

    own_images: list[Image] = Relationship(back_populates="owner")
    liked_images: list[Image] = Relationship(
        back_populates="liked_by",
        link_model=ImageLikes,
    )
