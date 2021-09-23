from flask import Blueprint

bp = Blueprint(
    "imgupload",
    __name__,
    template_folder="templates",
    static_folder="static",
    static_url_path="/static/imgupload",
)

from app.imgupload import routes
