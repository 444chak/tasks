"""This module contains the database models."""

from datetime import date
import uuid
import io
from dataclasses import dataclass
import sqlalchemy

engine = sqlalchemy.create_engine("sqlite:///database.db")
metadata = sqlalchemy.MetaData()


def create_database(force: bool = False) -> None:
    """Create the database."""
    if metadata.tables:
        if force:
            metadata.drop_all(engine)
        else:
            return False
    metadata.create_all(engine)


@dataclass
class Task:
    """A simple class to represent a task."""

    id: int
    task: str
    end_date: date
    done: bool = False
    guid: uuid.UUID = uuid.uuid4()

    def __post_init__(self):
        self.end_date = (
            date.fromisoformat(self.end_date)
            if isinstance(self.end_date, str)
            else self.end_date
        )
        self.done = self.done == "True" if isinstance(self.done, str) else self.done

        self.guid = uuid.UUID(self.guid) if isinstance(self.guid, str) else self.guid

    def __str__(self) -> str:
        text = io.StringIO()
        text.write(f"{self.id}. ")
        text.write(f"{'[X]' if self.done else '[ ]'} \t")
        text.write(f"📅 {self.end_date.strftime('%d/%m/%Y')} \t")
        text.write(f"📝 {self.task} \t")
        text.write(f"🔑 {self.guid}")
        return text.getvalue()

    def check(self) -> None:
        """Mark the task as done if it is not already, if it is, mark it as not done."""
        self.done = not self.done
        update_task(self.id, self.done)


tasks_table = sqlalchemy.Table(
    "tasks",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("task", sqlalchemy.String),
    sqlalchemy.Column("end_date", sqlalchemy.Date),
    sqlalchemy.Column("done", sqlalchemy.Boolean),
    sqlalchemy.Column(
        "uuid", sqlalchemy.Uuid(as_uuid=True), unique=True, default=uuid.uuid4()
    ),
)


def add_task(
    task: str, end_date: date, done: bool = False, guid: uuid.UUID = None
) -> bool:
    """Add a task to the database.
    Args:
        task (str): The task to add.
        end_date (date): The end date of the task.
        done (bool): The status of the task.
    Returns:
        bool: True if the task was added successfully, False otherwise.
    """
    if guid is None:
        guid = uuid.uuid4()
    obj = Task(None, task, end_date, done, guid)

    stmt = tasks_table.insert().values(
        task=obj.task, end_date=obj.end_date, done=obj.done, uuid=obj.guid
    )
    with engine.begin() as connection:
        connection.execute(stmt)
        return True


def remove_task(task_id: int) -> bool:
    """Remove a task from the database.
    Args:
        task_id (int): The id of the task to remove.
    Returns:
        bool: True if the task was removed successfully, False otherwise.
    """
    stmt = tasks_table.delete().where(tasks_table.c.id == task_id)
    with engine.begin() as connection:
        result = connection.execute(stmt)
        return result.rowcount > 0


def update_task(task_id: int, done: bool) -> bool:
    """Update the done status of a task.
    Args:
        task_id (int): The id of the task to update.
        done (bool): The new status of the task.
    Returns:
        bool: True if the task was updated successfully, False otherwise.
    """
    stmt = tasks_table.update().where(tasks_table.c.id == task_id).values(done=done)
    with engine.begin() as connection:
        result = connection.execute(stmt)
        return result.rowcount > 0


def get_task(task_id: int) -> tuple:
    """Get a task from the database.
    Args:
        task_id (int): The id of the task to get.
    Returns:
        tuple: The task if found, None otherwise.
    """
    stmt = tasks_table.select().where(tasks_table.c.id == task_id)
    with engine.begin() as connection:
        result = connection.execute(stmt)
        return result.fetchone()


def tasks_list() -> list:
    """Get all tasks from the database.
    Returns:
        list: The list of tasks.
    """
    stmt = tasks_table.select()
    with engine.begin() as connection:
        result = connection.execute(stmt)
        return result.fetchall()