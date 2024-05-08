"""CSV tasks package for importing and exporting tasks."""

import csv
import io
import dataclasses
from sqlalchemy.exc import IntegrityError
from toudou import models


def export_tasks(tasks: list[int] = None) -> str:
    """Export tasks to a CSV file.
    Args:
        tasks (list[int]): The list of tasks to export.
    Returns:
        str: The CSV content."""
    tasks_not_found = []
    if len(tasks) == 0:
        tasks_list = models.tasks_list()
    else:
        tasks_list = []
        for task in tasks:
            if models.get_task(task) is None:
                tasks_not_found.append(task)
            else:
                tasks_list.append(models.get_task(task))

    tasks_fieldsnames = [f.name for f in dataclasses.fields(models.Task)]

    output = io.StringIO()
    csvwriter = csv.DictWriter(output, fieldnames=tasks_fieldsnames)
    csvwriter.writeheader()

    for task in tasks_list:
        csvwriter.writerow(dict(zip(tasks_fieldsnames, task)))

    return output.getvalue(), tasks_not_found


def import_tasks(content: str) -> tuple[list]:
    """Import tasks from a CSV file.
    Args:
        content (str): The content of the CSV file.
    Returns:
        tuple: A tuple containing the added tasks and the skipped tasks."""
    reader = csv.reader(io.StringIO(content))
    tasks = list(reader)

    skippeds_tasks = []
    added_tasks = []
    for task in tasks:
        if task == [f.name for f in dataclasses.fields(models.Task)]:
            continue
        try:
            models.add_task(*task[1:])
            added_tasks.append(task)
        except (ValueError, IntegrityError) as e:
            skippeds_tasks.append(
                (
                    task,
                    (
                        "Task already exists."
                        if e.__class__ == IntegrityError
                        else "Invalid task."
                    ),
                )
            )

    return added_tasks, skippeds_tasks
