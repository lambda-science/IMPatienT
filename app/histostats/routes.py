import json
from flask_login import current_user, login_required
from flask import render_template, request, flash, redirect, url_for
from app import db
from app.histostats import bp


@bp.route("/histostats", methods=["GET", "POST"])
def statsindex():
    """Page for histo statistics page."""
    return render_template("histostats_index.html")
