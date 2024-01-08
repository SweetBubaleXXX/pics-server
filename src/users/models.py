from enum import StrEnum, auto
from typing import Optional

from sqlmodel import Enum, Field, SQLModel


class Role(StrEnum):
    USER = auto()
    EMPLOYEE = auto()
    ADMIN = auto()


class UserBase(SQLModel):
    username: str = Field(unique=True)
    role: Role = Field(sa_column=Enum(Role), default=Role.USER)
    disabled: bool = False


class UserRead(UserBase):
    id: int


class UserCreate(UserBase):
    password: str


class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    password: str
