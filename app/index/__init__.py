from flask import Blueprint

bp = Blueprint("index", __name__, template_folder="templates")

from app.index import routes
