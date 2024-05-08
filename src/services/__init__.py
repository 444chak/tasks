"""CSV tasks package for importing and exporting tasks."""

import csv
import io
import os
import click
import models


EXPORT_PATH = "exports/"


def export_tasks(tasks: list[int] = None) -> str:
    """
    Export tasks to a CSV file.
    Args:
        tasks (list[int]): The list of tasks to export.
    Returns:
        str: The CSV file containing the tasks."""
    if len(tasks) == 0:
        tasks = models.tasks_list()
    else:
        tasks = [models.get_task(task) for task in tasks]

    output = io.StringIO()
    csvwriter = csv.DictWriter(output, fieldnames=["id", "task", "end_date", "done"])

    csvwriter.writeheader()

    for task in tasks:
        csvwriter.writerow(
            {
                "id": task[0],
                "task": task[1],
                "end_date": task[2],
                "done": task[3],
            }
        )

    return output.getvalue()


def import_tasks(file="tasks.csv"):
    """Import tasks from a CSV file."""
    if file != "tasks.csv" and not file.endswith(".csv"):
        file += ".csv"

    file = f"{EXPORT_PATH}{file}"
    if not os.path.isfile(file):
        click.echo(f"File {file} does not exist.")
        return

    with open(file, "r", newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        tasks = list(reader)

    for task in tasks:
        print(task[1:])
        models.add_task(*task[1:])

    click.echo(f"Tasks imported from {file}")
