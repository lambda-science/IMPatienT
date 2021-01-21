from flask import Blueprint

bp = Blueprint('index', __name__)

from app.index import routes