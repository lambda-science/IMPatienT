from impatient.app.index import bp
from flask import render_template


@bp.route("/")
def index():
    """View function for the Index page

    Returns:
        str: HTML template for the Index page
    """
    return render_template("index.html")
