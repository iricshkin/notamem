import uuid
from datetime import datetime
from sqlalchemy import String, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from litestar.plugins.sqlalchemy import base
from typing import Optional, List

from src.postgres.models.users import User
from src.postgres.models.tasks import Task
from src.postgres.models.reminders import Reminder


class Note(base.UUIDAuditBase):
    __tablename__ = 'notes'

    title: Mapped[str] = mapped_column(String(100), nullable=False)
    content: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow, onupdate=datetime.utcnow
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey('users.id', ondelete='CASCADE'), index=True
    )
    user: Mapped['User'] = relationship(back_populates='notes')

    tasks: Mapped[List['Task']] = relationship(back_populates='note')
    reminders: Mapped[List['Reminder']] = relationship(back_populates='note')
