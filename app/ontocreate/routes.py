import os
import json
from flask import render_template, current_app, send_from_directory, request
from flask_login import login_required
from sqlalchemy.orm.attributes import flag_modified
from app import db
from app.ontocreate import bp
from app.ontocreate.forms import OntologyDescript
from app.models import ReportHisto
from app.historeport.onto_func import Ontology


@bp.route("/config/<path:filename>")
@login_required
def onto_json(filename):
    """Serve files located in patient subfolder inside folder"""
    return send_from_directory(current_app.config["CONFIG_FOLDER"], filename)


@bp.route("/ontocreate", methods=["GET", "POST"])
@login_required
def ontocreate():
    """View used to show and modify ontology tree"""
    form = OntologyDescript()
    return render_template("ontocreate.html", form=form)


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
        os.path.join(current_app.config["CONFIG_FOLDER"], "ontology.json"), "w"
    ) as json_file:
        json.dump(clean_tree, json_file, indent=4)

    # Update All Reports to the latest Version of ontology
    template_ontology = Ontology(clean_tree)
    for report in ReportHisto.query.all():
        current_report_ontology = Ontology(report.ontology_tree)
        updated_report_ontology = json.loads(
            json.dumps(current_report_ontology.update_ontology(template_ontology))
        )
        # Issue: SQLAlchemy not updating JSON https://stackoverflow.com/questions/42559434/updates-to-json-field-dont-persist-to-db

        report.ontology_tree = updated_report_ontology
        flag_modified(report, "ontology_tree")
    db.session.commit()
    return json.dumps({"success": True}), 200, {"ContentType": "application/json"}
