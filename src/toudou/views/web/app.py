"""Main module for tasks flask webapp."""

from datetime import date
import dataclasses
from flask import Flask, render_template, redirect, request, Response
import toudou.models as models
import toudou.services as services

app = Flask(__name__)


@app.route("/")
def index():
    """The main page of the webapp."""
    return render_template("index.html")


@app.route("/tasks")
@app.route("/tasks/<int:task_id>/<string:action>")
@app.route("/tasks/add", methods=["POST"])
def tasks(task_id: int = None, action: str = None) -> Response:
    """The tasks page of the webapp."""
    if task_id and action:
        if action == "done":
            models.update_task(task_id, not models.get_task(task_id)[3])
            return redirect("/tasks")
        if action == "remove":
            models.remove_task(task_id)
            return redirect("/tasks")

    if request.form:
        print(request.form)
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
    )


@app.route("/tasks/action", methods=["POST"])
def tasks_action() -> Response:
    """Perform an action on the tasks.
    Returns:
        Response: A redirect to the tasks page."""
    print(request.form["action"])
    print(request.files["file"])

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
def tasks_import():
    """Import tasks from a CSV file.

    Returns:
        Response: A redirect to the tasks page.
    """
    content = request.files["file"].read().decode("utf-8")
    services.import_tasks(content)

    return redirect("/tasks")
