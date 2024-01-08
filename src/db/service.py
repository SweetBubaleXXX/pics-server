from typing import Type
from pydantic import AnyUrl
from sqlalchemy import Pool
from sqlmodel import Session, SQLModel, create_engine


class Database:
    def __init__(
        self,
        db_url: str | AnyUrl,
        pool_type: Type[Pool] | None = None,
    ) -> None:
        self._engine = create_engine(str(db_url), poolclass=pool_type)

    def create_tables(self) -> None:
        SQLModel.metadata.create_all(self._engine)

    def session(self) -> Session:
        return Session(self._engine)
