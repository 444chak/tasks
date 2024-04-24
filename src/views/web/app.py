"""Main module for tasks flask webapp."""
from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
def index():
    """The main page of the webapp."""
    return "<h1>Hello World ! 🌍</h1>"
