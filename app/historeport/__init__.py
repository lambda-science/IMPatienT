from flask import Blueprint

bp = Blueprint(
    "historeport",
    __name__,
    template_folder="templates",
    static_folder="static",
    static_url_path="/static/historeport",
)

from app.historeport import routes
