import functools
from contextlib import asynccontextmanager

from fastapi import FastAPI

from .containers import Container


@asynccontextmanager
async def lifespan(container: Container, app: FastAPI):
    db = container.db()
    db.create_tables()

    yield


def create_app() -> FastAPI:
    container = Container()
    app = FastAPI(lifespan=functools.partial(lifespan, container))
    app.container = container
    return app
