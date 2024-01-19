from ..exceptions import NotFound


class UserNotFound(NotFound):
    pass


class UserAlreadyExists(Exception):
    def __init__(self, message: str = "User already exists", *args) -> None:
        super().__init__(message, *args)


class InvalidPassword(Exception):
    pass
