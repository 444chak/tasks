"""This file contains the configuration for the application."""
import os

config = {
    "DATABASE_URL" : os.getenv("TASKS_DATABASE_URL", ""),
    "DEBUG" : os.getenv("TASKS_DEBUG", "False") == "True",
}
