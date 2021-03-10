from app import db
from app.historeportv2 import bp
import os
from flask import Flask, render_template, session, current_app
from flask_login import current_user, login_required
from app.models import ReportHisto, User


@bp.route("/historeportv2", methods=["GET", "POST"])
@login_required
def historeportv2():
    """palceholder"""
    return render_template("historeportv2/historeportv2.html")
