from typing import Annotated, Iterator
from dependency_injector.wiring import inject, Provide
from fastapi import Depends
from sqlmodel import Session

from .service import Database
from ..containers import Container


@inject
def get_db_session(database: Database = Provide[Container.db]) -> Iterator[Session]:
    with database.session() as session:
        yield session


DBSession = Annotated[Session, Depends(get_db_session)]
