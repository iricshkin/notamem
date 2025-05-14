import uuid
from datetime import datetime
from sqlalchemy import String, ForeignKey, Text, Enum as SQLAlchemyEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from litestar.plugins.sqlalchemy import base
from typing import Optional, List

from src.postgres.models.users import User
from src.postgres.models.notes import Note
from src.postgres.models.reminders import Reminder


__all__ = ('Task',)


TaskStatusEnum = SQLAlchemyEnum(
    'pending',
    'in_progress',
    'complleted',
    'overdue',
    'canseled',
    name='task_status_enum',
)


class Task(base.UUIDAuditBase):
    __tablename__ = 'tasks'

    title: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[str] = mapped_column(TaskStatusEnum, nullable=False, index=True)
    due_date: Mapped[Optional[datetime]] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow, onupdate=datetime.utcnow
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey('users.id', ondelete='CASCADE'), index=True
    )
    user: Mapped['User'] = relationship('User', back_populates='tasks')

    note_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey('notes.id', ondelete='CASCADE')
    )
    note: Mapped[Optional['Note']] = relationship('Note', back_populates='tasks')

    reminders: Mapped[List['Reminder']] = relationship('Reminder', back_populates='task')
