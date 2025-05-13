from msgspec import Struct
from datetime import datetime

__all__ = (
    'UserCreate',
    'UserPatch',
)


class UserCreate(Struct, kw_only=True, omit_defaults=True):
    first_name: str
    last_name: str
    email: str
    created_at: datetime


class UserPatch(Struct, kw_only=True, omit_defaults=True):
    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None
