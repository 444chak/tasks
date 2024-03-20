"""The main module for the tasks package."""

import uuid
from dataclasses import dataclass
import click


@dataclass
class Task:
    """A simple class to represent a task."""
    id: uuid.UUID
    task: str


@click.group()
def cli():
    """A simple CLI for managing tasks."""


@cli.command()
@click.option("-t", "--task", prompt="Your task", help="The task to remember.")
def display(task: str):
    """Display a task."""
    todo = Task(uuid.uuid4(), task)
    click.echo(todo)



@click.command()
@click.option("--count", default=1)
@click.option("--name", prompt="Your name")
def hello(count, name):
    """Print hello NAME for COUNT times."""
    for _ in range(count):
        click.echo(f"Hello {name}!")
