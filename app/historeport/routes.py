from flask_login import current_user, login_required
from flask import render_template, request
import json
from app import db
from app.historeport import bp
from app.models import ReportHisto
from app.historeport.forms import ReportForm, OntologyDescriptPreAbs


@bp.route("/historeport", methods=["GET", "POST"])
@login_required
def historeport():
    """palceholder"""
    if request.args:
        report_request = ReportHisto.query.get(request.args.get("id"))
        if report_request is not None:
            form = ReportForm(patient_nom=report_request.patient_nom,
                              patient_prenom=report_request.patient_prenom,
                              naissance=report_request.naissance,
                              expert_id=report_request.expert_id,
                              biopsie_id=report_request.biopsie_id,
                              muscle_prelev=report_request.muscle_prelev,
                              age_biopsie=report_request.age_biopsie,
                              date_envoie=report_request.date_envoie,
                              ontology_tree=report_request.ontology_tree,
                              comment=report_request.comment,
                              conclusion=report_request.conclusion)
        else:
            form = ReportForm()
    else:
        form = ReportForm()

    form2 = OntologyDescriptPreAbs()
    radio_field = list(form2.presence_absence)

    if form.validate_on_submit():
        if request.args:
            report_entry = ReportHisto.query.get(request.args.get("id"))
            if report_entry is not None:
                form.populate_obj(report_entry)
                report_entry.expert_id = current_user.id
                db.session.commit()

        else:
            report_entry = ReportHisto()
            form.populate_obj(report_entry)
            report_entry.expert_id = current_user.id
            db.session.add(report_entry)
            db.session.commit()

    return render_template("historeport/historeport.html",
                           form=form,
                           form2=form2,
                           radio_field=radio_field)
