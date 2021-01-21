from flask import Blueprint

bp = Blueprint('ocr', __name__)

from app.ocr import routes