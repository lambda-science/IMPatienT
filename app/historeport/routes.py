from app import db
from app.historeport import bp
import os
from flask import Flask, render_template, session, current_app
from flask_login import current_user, login_required
from app.models import ReportHisto, User
from app.historeport.forms import ReportForm, OntologyDescriptPreAbs
import json


@bp.route("/historeport", methods=["GET", "POST"])
@login_required
def historeport():
    """palceholder"""
    form = ReportForm()
    form2 = OntologyDescriptPreAbs()
    if form.validate_on_submit():
        json_report_data = json.dumps(form.json_ontology_tree.data)
    return render_template("historeport/historeport.html",
                           form=form,
                           form2=form2)
