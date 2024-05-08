"""Main module for tasks flask webapp."""

from datetime import date
import dataclasses
from flask import Flask, render_template, redirect, request, Response
from toudou import models
from toudou import services

app = Flask(__name__)


@app.route("/")
def index() -> Response:
    """The index page of the webapp.

    Returns:
        Response: The index page.
    """
    return render_template("index.html", is_db=models.is_db())


@app.route("/tasks")
@app.route("/tasks/<int:task_id>/<string:action>")
@app.route("/tasks/add", methods=["POST"])
def tasks(task_id: int = None, action: str = None) -> Response:
    """The tasks page of the webapp

    Args:
        task_id (int, optional): The ID of the task. Defaults to None.
        action (str, optional): The action to perform on the task. Defaults to None.

    Returns:
        Response: The tasks page.
    """

    if not models.is_db():
        return redirect("/")

    if task_id and action:
        if action == "done":
            models.update_task(task_id, not models.get_task(task_id)[3])
            return redirect("/tasks")
        if action == "remove":
            models.remove_task(task_id)
            return redirect("/tasks")

    if request.form:
        if "title" in request.form and "end_date" in request.form:
            models.add_task(
                request.form["title"], date.fromisoformat(request.form["end_date"])
            )
            return redirect("/tasks")

    tasks_header = [f.name for f in dataclasses.fields(models.Task)]

    tasks_map = list(
        map(
            lambda x: dict(zip(tasks_header, x)),
            models.tasks_list(),
        )
    )

    return render_template(
        "tasks.html",
        tasks=tasks_map,
        today=date.today(),
        task_edit=task_id,
    )


@app.route("/tasks/edit", methods=["POST"])
def tasks_edit() -> Response:
    """Edit a task.

    Returns:
        Response: A redirect to the tasks page.
    """
    task_id = request.form["task_id"]

    task_obj = models.Task(
        request.form["task_id"],
        request.form["task"],
        date.fromisoformat(request.form["end_date"]),
        request.form["done"],
    )
    models.edit_task(task_id, task_obj)
    return redirect("/tasks")


@app.route("/tasks/action", methods=["POST"])
def tasks_action() -> Response:
    """Perform an action on the tasks.
    Returns:
        Response: A redirect to the tasks page."""
    return redirect(f"/tasks/{request.form['action']}", code=307)


@app.route("/tasks/download", methods=["POST"])
def tasks_download() -> Response:
    """Download the tasks list.

    Returns:
        Response: The CSV file containing the tasks.
    """
    return Response(
        services.export_tasks(list(map(int, request.form.getlist("tasks"))))[0],
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=tasks.csv"},
    )


@app.route("/tasks/delete", methods=["POST"])
def tasks_delete() -> Response:
    """Delete the selected tasks.

    Returns:
        Response: A redirect to the tasks page.
    """
    for task in request.form.getlist("tasks"):
        models.remove_task(int(task))
    return redirect("/tasks")


@app.route("/tasks/import", methods=["POST"])
def tasks_import() -> Response:
    """Import tasks from a CSV file.

    Returns:
        Response: A redirect to the tasks page.
    """
    content = request.files["file"].read().decode("utf-8")
    services.import_tasks(content)

    return redirect("/tasks")


@app.route("/init")
def init_db() -> Response:
    """Initialize the database.

    Returns:
        Response: A redirect to the index page."""
    models.create_database()
    return redirect("/")
