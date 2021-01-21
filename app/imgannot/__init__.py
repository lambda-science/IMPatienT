from flask import Blueprint

bp = Blueprint('imgannot', __name__)

from app.imgannot import routes