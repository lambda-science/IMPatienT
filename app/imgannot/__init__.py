from flask import Blueprint

bp = Blueprint("imgannot", __name__, template_folder="templates")

from app.imgannot import routes
