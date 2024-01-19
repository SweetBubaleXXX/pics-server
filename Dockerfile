FROM python:3.11-slim as builder

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /app

COPY pyproject.toml poetry.lock ./

RUN pip install poetry~=1.5

RUN --mount=type=cache,target=$POETRY_CACHE_DIR \
    poetry install --without dev --no-root

FROM python:3.11-slim

ENV PYTHONUNBUFFERED 1 \
    PYTHONDONTWRITEBYTECODE 1

WORKDIR /app

ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH"

COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}

COPY ./src ./src

CMD [ "gunicorn", "-c", "src/gunicorn.conf.py", "src.main:create_app()", "-k", "uvicorn.workers.UvicornWorker" ]
