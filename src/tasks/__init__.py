"""The main module for the tasks package."""

import re
from datetime import date
from dataclasses import dataclass
import click
import database



@dataclass
class Task:
    """A simple class to represent a task."""
    id: int
    task: str
    end_date: date
    done: bool = False

    def __post_init__(self):
        self.end_date = date.fromisoformat(self.end_date)


    def __str__(self):
        status = "[X]" if self.done else "[ ]"
        return f"{self.id}. {status} \t📅 {self.end_date.strftime('%d/%m/%Y')} \t📝 {self.task} "

    def check(self):
        """Mark the task as done if it is not already, if it is, mark it as not done."""
        self.done = not self.done
        database.update_task(self.id, self.done)

@click.group()
def cli():
    """A simple CLI for managing tasks."""



@cli.command()
def todo():
    """List all tasks."""
    click.echo("Tasks:")
    for task in database.tasks_list():
        click.echo(Task(*task))

@cli.command()
@click.option("-t", "--task", prompt="Your task", help="The task to remember.")
@click.option("-d", "--end_date", prompt="End date", help="The end date of the task.")
def add(task: str, end_date: str):
    """Add a task.
    TASK is the description of the task.
    END_DATE is the end date of the task in the format dd/mm/yyyy."""

    # TODO: faisable avec une fonction de click
    if not re.match(r"\d{2}\/\d{2}\/\d{4}", end_date):
        click.echo("The date must be in the format dd/mm/yyyy.")
        return
    day, month, year = map(int, end_date.split("/"))
    end_date = date(year, month, day)
    if end_date < date.today():
        click.echo("The date must be in the future.")
        return

    if database.add_task(task, end_date):
        click.echo("Task added ! ✅")
        click.echo(f"Task: {task}, End date: {end_date.strftime('%d/%m/%Y')}")

@cli.command()
@click.argument("task_id", type=int, required=True)
def remove(task_id: int):
    """Remove a task.
    TASK_ID is the number of the task to remove.
    If the task does not exist, an error message will be displayed.
    For knowing the task_id, use the list command."""
    if database.remove_task(task_id):
        click.echo(f"Task {task_id} removed ! ✅")
    else:
        click.echo(f"Task {task_id} not found ! ❌")

@cli.command()
@click.argument("task_id", type=int, required=True)
def done(task_id: int):
    """Mark a task as done.
    TASK_ID is the number of the task to mark as done.
    If the task does not exist, an error message will be displayed.
    For knowing the task_id, use the list command."""
    task = Task(*database.get_task(task_id))
    if task:
        task.check()
        click.echo(f"Task {task_id} updated ! ✅")
