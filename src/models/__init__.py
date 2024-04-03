"""This module contains the database models."""

from datetime import date
import sqlalchemy

engine = sqlalchemy.create_engine("sqlite:///database.db")
metadata = sqlalchemy.MetaData()

def create_database():
    """Create the database."""
    metadata.create_all(engine)

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
        task: str: The description of the task.
        end_date: date: The end date of the task.
        done: bool: The status of the task.
    """
    stmt = tasks_table.insert().values(
        task=task, end_date=end_date, done=done
    )
    with engine.begin() as connection:
        connection.execute(stmt)
        return True


def remove_task(task_id: int) -> bool:
    """Remove a task from the database.
        task_id: int: The id of the task to remove.
    """
    stmt = tasks_table.delete().where(tasks_table.c.id == task_id)
    with engine.begin() as connection:
        result = connection.execute(stmt)
        return result.rowcount > 0


def update_task(task_id: int, done: bool) -> bool:
    """Update the done status of a task.
        task_id: int: The id of the task to update.
        done: bool: The new status of the task.
    """
    stmt = tasks_table.update().where(tasks_table.c.id == task_id).values(done=done)
    with engine.begin() as connection:
        result = connection.execute(stmt)
        return result.rowcount > 0


def get_task(task_id: int) -> tuple:
    """Get a task from the database.
        task_id: int: The id of the task to get.
    """
    stmt = tasks_table.select().where(tasks_table.c.id == task_id)
    with engine.begin() as connection:
        result = connection.execute(stmt)
        return result.fetchone()


def tasks_list() -> list:
    """Show all tasks in the database."""
    stmt = tasks_table.select()
    with engine.begin() as connection:
        result = connection.execute(stmt)
        return result.fetchall()
