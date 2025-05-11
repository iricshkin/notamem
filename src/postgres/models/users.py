from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from litestar.plugins.sqlalchemy import base


class User(base.UUIDAuditBase):
    __tablename__ = 'users'
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), nullable=True)
    email: Mapped[str] = mapped_column(
        String(255), nullable=False, unique=True, index=True
    )
