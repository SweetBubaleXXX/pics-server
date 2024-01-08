import functools
from contextlib import asynccontextmanager

from fastapi import FastAPI

from .api.router import api_router
from .containers import Container
from .exceptions import setup_exception_handlers


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

    return app
