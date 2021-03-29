from flask import Blueprint

bp = Blueprint(
    "imgannot",
    __name__,
    template_folder="templates",
    static_folder="static",
    static_url_path="/static/imgannot",
)

from app.imgannot import routes
