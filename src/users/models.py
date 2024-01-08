from typing import Optional

from sqlmodel import Field, SQLModel


class UserBase(SQLModel):
    username: str
    disabled: bool = False


class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    password: str


class UserRead(UserBase):
    id: int


class UserCreate(UserBase):
    password: str
