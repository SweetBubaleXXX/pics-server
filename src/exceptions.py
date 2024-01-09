from fastapi import FastAPI, HTTPException, Request, status

from .users.exceptions import UserAlreadyExists, UserNotFound


def user_not_found_handler(request: Request, exc: UserNotFound):
    raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found") from exc


def user_already_exists_handler(request: Request, exc: UserAlreadyExists):
    raise HTTPException(status.HTTP_400_BAD_REQUEST, "User already exists") from exc


def setup_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(UserNotFound, user_not_found_handler)
    app.add_exception_handler(UserAlreadyExists, user_already_exists_handler)
