from flask import Blueprint

bp = Blueprint("ontocreate", __name__, template_folder="templates")

from app.ontocreate import routes
