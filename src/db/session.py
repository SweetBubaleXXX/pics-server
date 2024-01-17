from typing import Annotated, Iterator

from dependency_injector.wiring import Provide, inject
from fastapi import Depends
from sqlmodel import Session

from ..containers import Container
from .service import Database


@inject
def get_database(database: Database = Provide[Container.db]) -> Database:
    return database


def _get_session_manager() -> Session:
    return get_database().session()


def get_db_session(
    session_manager: Annotated[Session, Depends(_get_session_manager)],
) -> Iterator[Session]:
    with session_manager as session:
        yield session


DBSession = Annotated[Session, Depends(get_db_session)]
