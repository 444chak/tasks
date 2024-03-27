"""CSV tasks package for importing and exporting tasks."""
import csv
import os
import click
import database

EXPORT_PATH = "exports/"


def export_tasks(file='tasks.csv', tasks=None):
    """Export tasks to a CSV file."""

    if os.path.isfile(f"{EXPORT_PATH}//{file}"):
        click.echo("File already exists. Do you want to overwrite it? (y/n)")
        if input().lower() != "y":
            return

    if len(tasks) == 0:
        tasks = database.tasks_list()
    else:
        tasks = [database.get_task(task) for task in tasks]


    file = f"{EXPORT_PATH}{file}"
    try:
        with open(file, "w", newline="", encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerows(tasks)
    except FileNotFoundError:
        click.echo("Directory {EXPORT_PATH} does not exist. Creating it...")
        os.mkdir(EXPORT_PATH)
        with open(file, "w", newline="", encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerows(tasks)

    click.echo(f"Tasks exported to {file}")
