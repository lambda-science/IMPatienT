from flask import Blueprint

bp = Blueprint("historeport", __name__, template_folder="templates")

from app.historeport import routes
