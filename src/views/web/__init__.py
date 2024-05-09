"""This module is the entry point of the web application."""
from views.web.app import app


def run():
    """Run the web application."""
    app.run()


def rund():
    """Run the web application in debug mode."""
    app.run(debug=True)
