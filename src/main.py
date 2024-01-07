from contextlib import asynccontextmanager
from fastapi import FastAPI

from .containers import Container


@asynccontextmanager
async def lifespan(app: FastAPI):
    container = Container()

    db = container.db()
    await db.create_tables()

    yield


def create_app() -> FastAPI:
    app = FastAPI(lifespan=lifespan)
    return app
