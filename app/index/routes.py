from app.index import bp
from flask import render_template
from flask_login import login_required
from flask_login import current_user
from flask import flash
from flask import redirect
from flask import url_for


@bp.route("/")
def index():
    """View function for the Index page

    Returns:
        str: HTML template for the Index page
    """
    return render_template("index.html")


@bp.route("/export_data")
@login_required
def export_data():
    if current_user.get_task_in_progress("export_data"):
        flash(_("An export task is currently in progress"))
    else:
        current_user.launch_task("export_data", ("Exporting data..."))
        current_user.save()
    return redirect(url_for("index.index", username=current_user.username))
