import json
from flask_login import current_user, login_required
from flask import render_template, request, flash, redirect, url_for
from app import db
from app.historeport import bp
from app.models import ReportHisto
from app.historeport.forms import ReportForm, OntologyDescriptPreAbs, DeleteButton


@bp.route("/historeport", methods=["GET", "POST"])
@login_required
def histoindex():
    """Page for management of reports registered in database."""
    form = DeleteButton()
    report_history = ReportHisto.query.all()
    return render_template("histo_index.html", history=report_history, form=form)


@bp.route("/historeport/new", methods=["GET", "POST"])
@login_required
def historeport():
    """Page to create new histology report of modify already existing one."""
    # If args in URL, try to retrive report from DB and pre-fill it
    ontology_tree_exist = False
    if request.args:
        report_request = ReportHisto.query.get(request.args.get("id"))
        if report_request is not None:
            form = ReportForm(
                patient_nom=report_request.patient_nom,
                patient_prenom=report_request.patient_prenom,
                naissance=report_request.naissance,
                expert_id=report_request.expert_id,
                biopsie_id=report_request.biopsie_id,
                muscle_prelev=report_request.muscle_prelev,
                age_biopsie=report_request.age_biopsie,
                date_envoie=report_request.date_envoie,
                gene_diag=report_request.gene_diag,
                ontology_tree=report_request.ontology_tree,
                comment=report_request.comment,
                conclusion=report_request.conclusion,
            )
            if form.ontology_tree.data:
                ontology_tree_exist = True
        else:
            return redirect(url_for("historeport.histoindex"))
    # If no args: empty form
    else:
        with open("config/ontology.json") as f:
            empty_json_tree = json.load(f)
        form = ReportForm(ontology_tree=empty_json_tree)
    # Form for panel on the right with node description
    form2 = OntologyDescriptPreAbs()
    radio_field = list(form2.presence_absence)

    # On validation, save to database
    if form.validate_on_submit():
        # Update existing DB entry or create a new one (else)
        if request.args:
            report_entry = ReportHisto.query.get(request.args.get("id"))
            if report_entry is not None:
                form.populate_obj(report_entry)
                report_entry.expert_id = current_user.id
                db.session.commit()
                return redirect(url_for("historeport.histoindex"))

        else:
            report_entry = ReportHisto()
            form.populate_obj(report_entry)
            report_entry.expert_id = current_user.id
            db.session.add(report_entry)
            db.session.commit()
            return redirect(url_for("historeport.histoindex"))

    return render_template(
        "historeport.html",
        form=form,
        form2=form2,
        radio_field=radio_field,
        ontology_tree_exist=ontology_tree_exist,
    )


@bp.route("/delete_report/<id_report>", methods=["POST"])
@login_required
def delete_report(id_report):
    """Page delete a histology report from database with delete button."""
    form = DeleteButton()
    # Retrieve database entry and delete it if existing
    if form.validate_on_submit():
        report_form = ReportHisto.query.get(id_report)
        if report_form is None:
            flash("Report {} not found.".format(id), "danger")
            return redirect(url_for("histoindex"))
        db.session.delete(report_form)
        db.session.commit()
        flash("Deleted entry {}!".format(id_report), "success")
        return redirect(url_for("historeport.histoindex"))
    else:
        return redirect(url_for("historeport.histoindex"))
