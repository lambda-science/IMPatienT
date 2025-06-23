from flask import Blueprint

bp = Blueprint(
    "histostats",
    __name__,
    template_folder="templates",
    static_folder="static",
    static_url_path="/static/histostats",
)

from impatient.app.histostats import routes
