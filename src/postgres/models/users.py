from datetime import datetime
from sqlalchemy import String, CheckConstraint, Index
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
    username: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(
        String(255), nullable=False, unique=True, index=True
    )
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    tasks: Mapped[List['Task']] = relationship('Task', back_populates='user')
    notes: Mapped[List['Note']] = relationship('Note', back_populates='user')
    reminders: Mapped[List['Reminder']] = relationship('Reminder', back_populates='user')

    __table_args__ = (
        CheckConstraint('length(first_name) > 0', name='check_first_name_not_empty'),
        CheckConstraint('length(last_name) > 0', name='check_last_name_not_empty'),
        CheckConstraint('length(username) > 0', name='check_username_not_empty'),
        CheckConstraint('email LIKE "%@%.%"', name='check_email_format'),
        Index('idx_users_created_at', 'created_at'),
    )
