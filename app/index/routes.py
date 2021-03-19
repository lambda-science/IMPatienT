from flask import render_template
from app.index import bp


@bp.route("/")
def index():
    """View function to show index page"""
    return render_template("index/index.html")
