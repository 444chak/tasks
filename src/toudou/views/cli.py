"""The main module for the tasks CLI."""

import inspect
import os
from datetime import date, datetime
from sqlalchemy.exc import OperationalError
import click
import toudou.models as models
import toudou.services as services

EXPORT_PATH = "exports/"


@click.group()
def cli():
    """A simple CLI for managing tasks."""


@cli.command()
def init_db():
    """Create the database."""
    if not models.create_database():
        click.echo("Database already exists.")
        click.echo("Do you want to recreate it? (y/n)")
        if input().lower() == "y":
            click.echo("Database recreated ! ✅")
            return
        else:
            click.echo("Database not recreated.")
            return
    click.echo("Creating the database...")
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
@click.option("-t", "--task", help="Get a specific task by ID.", type=int, prompt=True)
def get(task: int):
    """Get a specific task by ID.
    TASK is the ID of the task to get."""
    try:
        task_obj = models.get_task(task)
        if task_obj:
            click.echo(models.Task(*task_obj))
        else:
            click.echo(f"Task {task} not found ! ❌")
            click.echo("For knowing the task_id, use 'todo' command.")
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
def testadd():
    """Add a test task."""
    try:
        if models.add_task("Test task", date.today()):
            click.echo("Task added ! ✅")
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
        try:
            models.Task(*models.get_task(task_id)).check()
            click.echo(f"Task {task_id} updated ! ✅")
        except TypeError:
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
                export = services.export_tasks(tasks)
                f.write(export[0])
        except FileNotFoundError:
            click.echo("Directory {EXPORT_PATH} does not exist. Creating it...")
            os.mkdir(EXPORT_PATH)
            with open(file, "w", newline="", encoding="utf-8") as f:
                export = services.export_tasks(tasks)
                f.write(export[0])
        click.echo(f"Tasks exported to {file} ! ✅")
        click.echo(f"Tasks not found: {export[1]}")

    except OperationalError:
        error_db()


@cli.command()
# @click.option("-f", "--file", help="The file to import from.", required=True)
@click.argument("file", type=click.File("r"))
def timport(file: click.File):
    """Import tasks from a file.
    USAGE: timport FILE
    FILE is the file to import from."""
    try:
        valid, invalid = services.import_tasks(file.read())
        services.import_tasks(file.read())
        if valid:
            click.echo(f"Tasks imported from {file.name} ! ✅")
            click.echo("Tasks importeds:")
            for task in valid:
                click.echo(models.Task(*task))
        if invalid:
            if not valid:
                click.echo("No tasks imported. ❌")
            click.echo("Invalid tasks:")
            for task in invalid:
                click.echo(
                    f"Task name: {task[0][1]}, End date: {task[0][2]}, GUID: {task[0][3]} - "
                    + click.style("Error: ", fg="red")
                    + click.style(task[1], fg="yellow")
                )

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
    click.echo("You can do it by running the command: init-db")
