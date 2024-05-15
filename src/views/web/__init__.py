"""This module is the entry point of the web application."""
from flask import Flask
from views.web.app import ui

def create_app() -> None:
    """Create the webapp."""

    app = Flask(__name__)

    app.register_blueprint(ui)
    return app
