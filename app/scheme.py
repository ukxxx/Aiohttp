from abc import ABC
from typing import Optional, Type

import pydantic


class AbstractAdvert(pydantic.BaseModel, ABC):
    name: str
    description: str
    owner_id: int

    @pydantic.field_validator("name")
    @classmethod
    def name_length(cls, v):
        if len(v) > 100:
            raise ValueError("Name must be no longer 100 characters")
        return v

    @pydantic.field_validator("description")
    @classmethod
    def description_length(cls, v):
        if len(v) > 100:
            raise ValueError("Description must be no longer 100 characters")
        return v


class CreateAdvert(AbstractAdvert):
    name: str
    description: str
    owner_id: int


class UpdateAdvert(AbstractAdvert):
    name: Optional[str] = None
    description: Optional[str] = None
    owner_id: Optional[int] = None


class AbstractUser(pydantic.BaseModel, ABC):
    mail: str
    password: str

    @pydantic.field_validator("mail")
    @classmethod
    def mail_length(cls, v):
        if len(v) > 100:
            raise ValueError("Email must be no longer 100 characters")
        return v

    @pydantic.field_validator("password")
    @classmethod
    def password_length(cls, v):
        if len(v) > 100:
            raise ValueError("Password must be no longer 100 characters")
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v


class CreateUser(AbstractUser):
    mail: str
    password: str


SCHEME_CLASS = Type[CreateAdvert | UpdateAdvert | CreateUser]
SCHEME = CreateAdvert | UpdateAdvert | CreateUser
