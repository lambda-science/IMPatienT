from flask import Blueprint

bp = Blueprint("ocr", __name__, template_folder="templates")

from app.ocr import routes
