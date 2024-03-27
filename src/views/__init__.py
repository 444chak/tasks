"""The main module for the tasks package."""

from datetime import date, datetime
from dataclasses import dataclass
import click
import models
import services


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
        models.update_task(self.id, self.done)


@click.group()
def cli():
    """A simple CLI for managing tasks."""


@cli.command()
def todo():
    """List all tasks."""
    click.echo("Tasks:")
    for task in models.tasks_list():
        click.echo(Task(*task))


@cli.command()
@click.option("-t", "--task", prompt="Your task", help="The task to remember.")
@click.option(
    "-d",
    "--end_date",
    prompt="End date",
    help="The end date of the task.",
    type=click.DateTime(["%d/%m/%Y"]),
)
def add(task: str, end_date: datetime):
    """Add a task.
    TASK is the description of the task.
    END_DATE is the end date of the task in the format dd/mm/yyyy."""
    end_date = end_date.date()

    if end_date < date.today():
        click.echo("The date must be in the future.")
        return

    if models.add_task(task, end_date):
        click.echo("Task added ! ✅")
        click.echo(f"Task: {task}, End date: {end_date.strftime('%d/%m/%Y')}")


@cli.command()
@click.argument("task_id", type=int, required=True, nargs=-1)
def remove(task_id: int):
    """Remove a task.
    USAGE: remove TASK_ID [TASK_ID...]

    TASK_ID is the number of the task to remove.
    If the task does not exist, an error message will be displayed.
    For knowing the task_id, use the list command."""
    if len(task_id) > 1:
        for task in task_id:
            if models.remove_task(task):
                click.echo(f"Task {task} removed ! ✅")
            else:
                click.echo(f"Task {task} not found ! ❌")
        return
    else:
        task_id = task_id[0]
    if models.remove_task(task_id):
        click.echo(f"Task {task_id} removed ! ✅")
    else:
        click.echo(f"Task {task_id} not found ! ❌")


@cli.command()
@click.argument("task_id", type=int, required=True, nargs=-1)
def done(task_id: int):
    """Mark a task as done.
    USAGE: done TASK_ID
    TASK_ID is the number of the task to mark as done.
    If the task does not exist, an error message will be displayed.
    For knowing the task_id, use the list command."""
    if len(task_id) > 1:
        for task in task_id:
            task = Task(*models.get_task(task))
            if task:
                task.check()
                click.echo(f"Task {task_id} updated ! ✅")
            else:
                click.echo(f"Task {task_id} not found ! ❌")
        return
    else:
        task_id = task_id[0]
    task = Task(*models.get_task(task_id))
    if task:
        task.check()
        click.echo(f"Task {task_id} updated ! ✅")
    else:
        click.echo(f"Task {task_id} not found ! ❌")


@cli.command()
@click.option("-f", "--file", help="The file to export to.", default="tasks.csv")
@click.argument("tasks", type=int, nargs=-1, required=False)
def texport(file: str, tasks):
    """Export tasks to a file.
    USAGE: texport FILE [TASKS...]
    FILE is the file to export to.
    TASKS are the tasks to export. If not specified, all tasks will be exported."""
    if not tasks:
        click.echo("No tasks specified. Exporting all tasks.")
    print(file)
    services.export_tasks(file, tasks)


@cli.command()
@click.option("-f", "--file", help="The file to import from.", required=True)
def timport(file: str):
    """Import tasks from a file.
    USAGE: timport FILE
    FILE is the file to import from."""
    services.import_tasks(file)
