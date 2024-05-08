"""Main module for tasks flask webapp."""

from datetime import date
from flask import Flask, render_template, redirect, request, Response
import models
import services

app = Flask(__name__)


@app.route("/")
def index():
    """The main page of the webapp."""
    return render_template("index.html")


@app.route("/tasks")
@app.route("/tasks/<int:task_id>/<string:action>")
@app.route("/tasks/add", methods=["POST"])
def tasks(task_id: int = None, action: str = None):
    """The tasks page of the webapp."""
    if task_id and action:
        if action == "done":
            models.update_task(task_id, not models.get_task(task_id)[3])
            return redirect("/tasks")
        if action == "remove":
            models.remove_task(task_id)
            return redirect("/tasks")

    if request.form:
        models.add_task(
            request.form["title"], date.fromisoformat(request.form["end_date"])
        )
        return redirect("/tasks")

    # tasks_header = ["id", "title", "end_date", "done"]

    # tasks_map = list(
    #     map(
    #         lambda x: dict(zip(tasks_header, x)),
    #         models.tasks_list(),
    #     )
    # )

    # print(tasks_map)

    return render_template(
        "tasks.html",
        tasks=list(
            map(
                lambda x: dict(zip(["id", "title", "end_date", "done"], x)),
                models.tasks_list(),
            )
        ),
        today=date.today(),
    )


@app.route("/tasks/download", methods=["POST"])
def tasks_download() -> Response:
    """Download the tasks list.

    Returns:
        Response: The CSV file containing the tasks.
    """


    return Response(
        services.export_tasks(list(map(int, request.form.getlist("tasks")))),
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=tasks.csv"},
    )
