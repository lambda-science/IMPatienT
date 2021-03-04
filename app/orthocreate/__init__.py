from flask import Blueprint

bp = Blueprint('orthocreate', __name__)

from app.orthocreate import routes