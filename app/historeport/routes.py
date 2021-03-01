from app import db
from app.historeport import bp
from app.historeport.forms import ReportForm
import app.historeport.report as Report
import os
from flask import Flask, render_template, session, current_app
from flask_login import current_user, login_required
from app.models import ReportHisto, User


@bp.route("/historeport", methods=["GET", "POST"])
@login_required
def historeport():
    """palceholder"""
    titre_colonnes = Report.generate_historeportForm(
        ReportForm, os.path.join("config", "report_form_config.tsv"))
    form = ReportForm()
    liste_caract = list(form.__dict__["_fields"].keys())
    liste_caract = liste_caract[7:-4]

    if form.validate_on_submit():
        liste_fields = list(form.__dict__["_fields"].keys())
        liste_fields = liste_fields[:-2]
        report = ReportHisto()
        setattr(report, "expert_id", current_user.id)
        for i in liste_fields:
            setattr(report, i, form[i].data)

        db.session.add(report)
        db.session.commit()
    return render_template("historeport/historeport.html",
                           form=form,
                           titre_colonnes=titre_colonnes,
                           liste_caract=liste_caract)
