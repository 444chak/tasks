"""The main module for the tasks CLI."""

import inspect
import os
from datetime import date, datetime
from sqlalchemy.exc import OperationalError
import click
import models
import services

EXPORT_PATH = "exports/"


@click.group()
def cli():
    """A simple CLI for managing tasks."""


@cli.command()
def init_db():
    """Create the database."""
    click.echo("Creating the database...")
    models.create_database()
    click.echo("Database created ! ✅")


@cli.command()
def todo():
    """List all tasks."""
    try:
        click.echo("Tasks:")
        for task in models.tasks_list():
            click.echo(models.Task(*task))
    except OperationalError:
        error_db()


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

    try:
        if models.add_task(task, end_date):
            click.echo("Task added ! ✅")
            click.echo(f"Task: {task}, End date: {end_date.strftime('%d/%m/%Y')}")

    except OperationalError:
        error_db()


@cli.command()
@click.argument("task_id", type=int, required=True, nargs=-1)
def remove(task_id: int):
    """Remove a task.
    USAGE: remove TASK_ID [TASK_ID...]

    TASK_ID is the number of the task to remove.
    If the task does not exist, an error message will be displayed.
    For knowing the task_id, use the list command."""
    try:
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
    except OperationalError:
        error_db()


@cli.command()
@click.argument("task_id", type=int, required=True, nargs=-1)
def done(task_id: int):
    """Mark a task as done.
    USAGE: done TASK_ID
    TASK_ID is the number of the task to mark as done.
    If the task does not exist, an error message will be displayed.
    For knowing the task_id, use the list command."""
    try:
        if len(task_id) > 1:
            for task in task_id:
                task = models.Task(*models.get_task(task))
                if task:
                    task.check()
                    click.echo(f"Task {task_id} updated ! ✅")
                else:
                    click.echo(f"Task {task_id} not found ! ❌")
            return
        else:
            task_id = task_id[0]
        task = models.Task(*models.get_task(task_id))
        if task:
            task.check()
            click.echo(f"Task {task_id} updated ! ✅")
        else:
            click.echo(f"Task {task_id} not found ! ❌")
    except OperationalError:
        error_db()


@cli.command()
@click.option(
    "-f",
    "--file",
    help="The file to export to.",
    show_default=True,
    default="tasks.csv",
    prompt=True,
)
@click.argument(
    "tasks",
    type=int,
    nargs=-1,
    required=False,
)
def texport(file: str, tasks: list[int]):
    """Export tasks to a file.
    USAGE: texport [--file FILE] [TASKS...]
    FILE is the file to export to.
    TASKS are the tasks to export. If not specified, all tasks will be exported."""
    if not tasks:
        click.echo("No tasks specified. Exporting all tasks.")
        click.echo(
            "If you want to export only specific tasks, use 'texport FILE TASK_ID [TASK_ID...]'"
        )
    try:
        if file != "tasks.csv" and not file.endswith(".csv"):
            file += ".csv"

        if os.path.isfile(f"{EXPORT_PATH}//{file}"):
            click.echo("File already exists. Do you want to overwrite it? (y/n)")
            if input().lower() != "y":
                return

        file = f"{EXPORT_PATH}{file}"

        try:
            with open(file, "w", newline="", encoding="utf-8") as f:
                f.write(services.export_tasks(tasks))

            click.echo(f"Tasks exported to {file} ! ✅")
        except FileNotFoundError:
            click.echo("Directory {EXPORT_PATH} does not exist. Creating it...")
            os.mkdir(EXPORT_PATH)
            with open(file, "w", newline="", encoding="utf-8") as f:
                f.write(services.export_tasks(tasks))

    except OperationalError:
        error_db()


@cli.command()
@click.option("-f", "--file", help="The file to import from.", required=True)
def timport(file: str):
    """Import tasks from a file.
    USAGE: timport FILE
    FILE is the file to import from."""
    try:
        services.import_tasks(file)
    except OperationalError:
        error_db()


def error_db():
    """Display an error message if the database is not initialized."""
    click.echo(
        click.style("ERROR: ", fg="red", bold=True)
        + "A database error occurred with "
        + click.style(inspect.stack()[1][3], fg="yellow", bold=True)
        + "."
    )
    click.echo("Do you have the database initialized ?")
    click.echo("You can do it by running the command: init_db")
