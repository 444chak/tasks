"""Main module for tasks flask webapp."""
from flask import Flask, render_template
import models
import services

app = Flask(__name__)


@app.route("/")
def index():
    """The main page of the webapp."""
    return render_template("index.html")

@app.route("/tasks")
def tasks():
    """The tasks page of the webapp."""

    rows_header = ["id", "title", "end_date", "done"]

    tasks_map = list(map(lambda x: dict(zip(rows_header , x)), models.tasks_list()))


    return render_template("tasks.html", tasks=list(map(lambda x: dict(zip(["id", "title", "end_date", "done"] , x)), models.tasks_list())))