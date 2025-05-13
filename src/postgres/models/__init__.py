from postgres.models.reminders import Reminder
from postgres.models.tasks import Task
from postgres.models.notes import Note
from postgres.models.users import User

__all__ = ['Reminder', 'Task', 'Note', 'User']

from sqlalchemy.orm import configure_mappers

configure_mappers()
