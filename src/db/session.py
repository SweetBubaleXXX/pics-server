from typing import Annotated, Iterator

from dependency_injector.wiring import Provide, inject
from fastapi import Depends
from sqlmodel import Session

from ..containers import Container
from .service import Database


@inject
def get_db_session(
    database: Annotated[Database, Depends(Provide[Container.db])],
) -> Iterator[Session]:
    with database.session() as session:
        yield session


DBSession = Annotated[Session, Depends(get_db_session)]
