import uuid
from datetime import datetime
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from litestar.plugins.sqlalchemy import base
from typing import Optional

from src.postgres.models.users import User
from src.postgres.models.tasks import Task
from src.postgres.models.notes import Note


__all__ = ('Reminder',)


class Reminder(base.UUIDAuditBase):
    __tablename__ = 'reminders'

    title: Mapped[str] = mapped_column(String(100), nullable=False)
    reminder_time: Mapped[datetime] = mapped_column(nullable=False)
    is_send: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    # from src.postgres.models.users import User
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey('users.id', ondelete='CASCADE'), index=True
    )
    user: Mapped['User'] = relationship('User', back_populates='reminders')

    # from src.postgres.models.tasks import Task
    task_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey('tasks.id', ondelete='CASCADE'), index=True
    )
    task: Mapped[Optional['Task']] = relationship('Task', back_populates='reminders')

    # from src.postgres.models.notes import Note
    note_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey('notes.id', ondelete='CASCADE'), index=True
    )
    note: Mapped[Optional['Note']] = relationship('Note', back_populates='reminders')
