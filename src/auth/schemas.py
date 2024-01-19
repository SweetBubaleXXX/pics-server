from pydantic import BaseModel, Field

from ..users.models import PASSWORD_CONSTRAINTS, USERNAME_CONSTRAINTS


class LoginSchema(BaseModel):
    username: str = Field(**USERNAME_CONSTRAINTS, pattern=r"^\w+$")
    password: str = Field(**PASSWORD_CONSTRAINTS)


class RegistrationSchema(LoginSchema):
    pass


class PasswordUpdateSchema(BaseModel):
    current_password: str = Field(**PASSWORD_CONSTRAINTS)
    new_password: str = Field(**PASSWORD_CONSTRAINTS)
