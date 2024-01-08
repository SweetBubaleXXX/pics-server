from enum import StrEnum, auto
from typing import Optional

from sqlmodel import Enum, Field, SQLModel

USERNAME_CONSTRAINTS = dict(min_length=5, max_length=20)
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


class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    password: str
