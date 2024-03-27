"""Database module for the application."""

from datetime import date
import sqlite3
import click

DATABASE = sqlite3.connect("database.db")



def init() -> None:
    """Initialize the database."""
    DATABASE.execute(
        "CREATE TABLE IF NOT EXISTS tasks (id INTEGER PRIMARY KEY, task TEXT, end_date DATE, done BOOLEAN)"
    )
    DATABASE.commit()
    click.echo("Initialized the database.")

if DATABASE.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall() == []:
    init()

def show_tables() -> list:
    """Show all tables in the database."""
    cursor = DATABASE.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    return cursor.fetchall()


def add_task(task: str, end_date: date, done: bool = False) -> bool:
    """Add a task to the database."""
    try:
        DATABASE.execute(
            "INSERT INTO tasks (task, end_date, done) VALUES (?, ?, ?)",
            (task, end_date, done),
        )
        DATABASE.commit()
        return True
    except sqlite3.Error as e:
        click.echo(f"An error occurred: {e}")
        return False

def remove_task(task_id: int) -> bool:
    """Remove a task from the database."""
    try:
        cursor = DATABASE.cursor()
        cursor.execute("DELETE FROM tasks WHERE id=?", (task_id,))
        if cursor.rowcount == 0:
            return False
        DATABASE.commit()
        return True
    except sqlite3.Error as e:
        click.echo(f"An error occurred: {e}")
        return False

def update_task(task_id: int, done: bool) -> bool:
    """Update the done status of a task."""
    try:
        DATABASE.execute("UPDATE tasks SET done=? WHERE id=?", (done, task_id))
        DATABASE.commit()
        return True
    except sqlite3.Error as e:
        click.echo(f"An error occurred: {e}")
        return False

def get_task(task_id: int) -> tuple:
    """Get a task from the database."""
    cursor = DATABASE.cursor()
    cursor.execute("SELECT * FROM tasks WHERE id=?", (task_id,))
    return cursor.fetchone()

def tasks_list() -> list:
    """Show all tasks in the database."""
    cursor = DATABASE.cursor()
    cursor.execute("SELECT * FROM tasks")
    return cursor.fetchall()
