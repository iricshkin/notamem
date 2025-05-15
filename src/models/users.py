from msgspec import Struct
from datetime import datetime

__all__ = (
    'UserLogin',
    'UserCreate',
    'UserRead',
    'UserPatch',
)


class UserLogin(Struct, kw_only=True):
    username: str
    password: str


class UserCreate(Struct, kw_only=True):
    first_name: str
    last_name: str
    username: str
    email: str
    password: str


class UserRead(Struct, kw_only=True):
    id: str
    first_name: str
    last_name: str
    username:str
    email: str
    created_at: datetime


class UserPatch(Struct, kw_only=True, omit_defaults=True):
    first_name: str | None = None
    last_name: str | None = None
    username: str | None = None
    email: str | None = None
    password: str | None = None
