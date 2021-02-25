from app import db
from app.historeport import bp

from flask import Flask, render_template, session, current_app
from flask_login import current_user, login_required


@bp.route("/historeport", methods=["GET", "POST"])
@login_required
def historeport():
    """palceholder"""
    # Show Image History
    return render_template("historeport/historeport.html")