"""This module contains the database models."""

from datetime import date
from dataclasses import dataclass
import sqlalchemy

engine = sqlalchemy.create_engine("sqlite:///database.db")
metadata = sqlalchemy.MetaData()


def create_database():
    """Create the database."""
    metadata.create_all(engine)


@dataclass
class Task:
    """A simple class to represent a task."""

    id: int
    task: str
    end_date: date
    done: bool = False

    def __str__(self) -> str:
        status = "[X]" if self.done else "[ ]"
        return f"{self.id}. {status} \t📅 {self.end_date.strftime('%d/%m/%Y')} \t📝 {self.task} "

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
)


def add_task(task: str, end_date: date, done: bool = False) -> bool:
    """Add a task to the database.
    Args:
        task (str): The task to add.
        end_date (date): The end date of the task.
        done (bool): The status of the task.
    Returns:
        bool: True if the task was added successfully, False otherwise.
    """
    stmt = tasks_table.insert().values(task=task, end_date=end_date, done=done)
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
