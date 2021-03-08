from flask import Blueprint

bp = Blueprint('onthocreate', __name__)

from app.onthocreate import routes