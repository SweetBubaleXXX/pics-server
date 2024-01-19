import functools
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request, status
from fastapi_pagination import add_pagination

from .api.router import api_router
from .containers import Container
from .exceptions import NotFound
from .users.exceptions import UserAlreadyExists


def not_found_handler(request: Request, exc: NotFound):
    raise HTTPException(status.HTTP_404_NOT_FOUND, str(exc)) from exc


def user_already_exists_handler(request: Request, exc: UserAlreadyExists):
    raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc)) from exc


def setup_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(NotFound, not_found_handler)
    app.add_exception_handler(UserAlreadyExists, user_already_exists_handler)


@asynccontextmanager
async def lifespan(container: Container, app: FastAPI):
    db = container.db()
    db.create_tables()

    yield


def create_app() -> FastAPI:
    container = Container()
    app = FastAPI(lifespan=functools.partial(lifespan, container))
    app.container = container

    setup_exception_handlers(app)

    app.include_router(api_router)

    add_pagination(app)

    return app
