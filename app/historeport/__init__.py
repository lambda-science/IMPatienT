from flask import Blueprint

bp = Blueprint("historeport", __name__)

from app.historeport import routes
