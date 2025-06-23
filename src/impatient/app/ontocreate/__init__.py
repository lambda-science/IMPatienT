from flask import Blueprint

bp = Blueprint(
    "ontocreate",
    __name__,
    template_folder="templates",
    static_folder="static",
    static_url_path="/static/ontocreate",
)

from impatient.app.ontocreate import routes
