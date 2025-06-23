from flask import Blueprint

bp = Blueprint(
    "dashapp",
    __name__,
    template_folder="templates",
    static_folder="static",
    static_url_path="/static/dashapp",
)

from impatient.app.dashapp import routes
