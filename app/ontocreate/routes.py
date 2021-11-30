import os
import json
from flask import (
    render_template,
    current_app,
    send_from_directory,
    request,
    redirect,
    url_for,
)
from flask_login import login_required
from sqlalchemy.orm.attributes import flag_modified
from app import db
from app.ontocreate import bp
from app.ontocreate.forms import OntologyDescript, InvertLangButton
from app.models import ReportHisto
from app.historeport.onto_func import StandardVocabulary


@bp.route("/ontology/<path:filename>")
@login_required
def onto_json(filename):
    """Serve ontology json file"""
    return send_from_directory(current_app.config["ONTOLOGY_FOLDER"], filename)


@bp.route("/ontocreate", methods=["GET", "POST"])
@login_required
def ontocreate():
    """View used to show and modify ontology tree"""
    form = OntologyDescript()
    form2 = InvertLangButton()
    return render_template("ontocreate.html", form=form, form2=form2)


@bp.route("/modify_onto", methods=["PATCH"])
@login_required
def modify_onto():
    """Update ontology json file with PATCH Ajax Request from JSTree"""
    # Get AJAX JSON data and parse it
    raw_data = request.get_data()
    parsed = json.loads(raw_data)
    dirty_tree = {
        i["id"]: {
            "id": i["id"],
            "text": i["text"],
            "icon": i["icon"],
            "data": i["data"],
            "parent": i["parent"],
        }
        for i in parsed
    }
    clean_tree = []
    for i in dirty_tree:
        clean_tree.append(dirty_tree[i])
    with open(
        os.path.join(current_app.config["ONTOLOGY_FOLDER"], "ontology.json"), "w"
    ) as json_file:
        json.dump(clean_tree, json_file, indent=4)

    # Update All Reports to the latest Version of ontology
    template_ontology = StandardVocabulary(clean_tree)
    for report in ReportHisto.query.all():
        current_report_ontology = StandardVocabulary(report.ontology_tree)
        updated_report_ontology = json.loads(
            json.dumps(current_report_ontology.update_ontology(template_ontology))
        )
        # Issue: SQLAlchemy not updating JSON https://stackoverflow.com/questions/42559434/updates-to-json-field-dont-persist-to-db

        report.ontology_tree = updated_report_ontology
        flag_modified(report, "ontology_tree")
    db.session.commit()

    # Update The DashApp Callback & layout
    # By Force reloading the layout code
    dashapp = current_app.config["DASHAPP"]
    with current_app.app_context():
        import importlib
        import app.dashapp.layout

        importlib.reload(app.dashapp.layout)
        dashapp.layout = app.dashapp.layout.layout
    return json.dumps({"success": True}), 200, {"ContentType": "application/json"}


@bp.route("/download_onto", methods=["GET"])
@login_required
def download_onto():
    """Download ontology tree"""
    return send_from_directory(
        current_app.config["ONTOLOGY_FOLDER"], "ontology.json", as_attachment=True
    )


@bp.route("/invert_lang", methods=["POST"])
@login_required
def invert_lang():
    """Download ontology tree"""

    # Open the ontology, invert text and alternative field, save it
    with open(
        os.path.join(current_app.config["ONTOLOGY_FOLDER"], "ontology.json"), "r"
    ) as fp:
        onto = json.load(fp)

    for term in onto:
        if term["data"]["alternative_language"] != "":
            temp_term = term["text"]
            term["text"] = term["data"]["alternative_language"]
            term["data"]["alternative_language"] = temp_term

    with open(
        os.path.join(current_app.config["ONTOLOGY_FOLDER"], "ontology.json"), "w"
    ) as fp:
        json.dump(onto, fp, indent=4)

    # After Switching lang, switch it for all patients onto_tree !
    template_ontology = StandardVocabulary(onto)
    for report in ReportHisto.query.all():
        current_report_ontology = StandardVocabulary(report.ontology_tree)
        updated_report_ontology = json.loads(
            json.dumps(current_report_ontology.update_ontology(template_ontology))
        )
        # Issue: SQLAlchemy not updating JSON https://stackoverflow.com/questions/42559434/updates-to-json-field-dont-persist-to-db

        report.ontology_tree = updated_report_ontology
        flag_modified(report, "ontology_tree")
    db.session.commit()
    return redirect(url_for("ontocreate.ontocreate"))
