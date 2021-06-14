from flask import Blueprint

bp = Blueprint(
    "dashapp",
    __name__,
    template_folder="templates",
    static_folder="static",
    static_url_path="/static/dashapp",
)

from app.dashapp import routes
