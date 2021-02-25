from app import db
from app.historeport import bp
from app.historeport.forms import ReportForm
import app.historeport.report as Report
import os
from flask import Flask, render_template, session, current_app
from flask_login import current_user, login_required


@bp.route("/historeport", methods=["GET", "POST"])
@login_required
def historeport():
    """palceholder"""
    Report.generate_historeportForm(ReportForm, os.path.join("config", "report_form_config.tsv"))
    form = ReportForm()
    return render_template("historeport/historeport.html", form=form)