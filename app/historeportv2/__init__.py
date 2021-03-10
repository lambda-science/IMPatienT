from flask import Blueprint

bp = Blueprint('historeportv2', __name__)

from app.historeportv2 import routes