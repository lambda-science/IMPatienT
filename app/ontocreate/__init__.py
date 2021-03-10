from flask import Blueprint

bp = Blueprint('ontocreate', __name__)

from app.ontocreate import routes