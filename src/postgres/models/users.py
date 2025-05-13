from datetime import datetime
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from litestar.plugins.sqlalchemy import base
from typing import List

from src.postgres.models.tasks import Task
from src.postgres.models.notes import Note
from src.postgres.models.reminders import Reminder


__all__ = ('User',)


class User(base.UUIDAuditBase):
    __tablename__ = 'users'

    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(
        String(255), nullable=False, unique=True, index=True
    )
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    tasks: Mapped[List['Task']] = relationship(back_populates='user')
    notes: Mapped[List['Note']] = relationship(back_populates='user')
    reminders: Mapped[List['Reminder']] = relationship(back_populates='user')
