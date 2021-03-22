import os
import json
from flask import render_template, current_app, send_from_directory, request
from flask_login import login_required
from app.ontocreate import bp
from app.ontocreate.forms import OntologyDescript


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
    return render_template("ontocreate/ontocreate.html", form=form)


@bp.route("/modify_onto", methods=["PATCH"])
@login_required
def modify_onto():
    """Update ontology json file with PATCH Ajax Request from JSTree"""
    # Get AJAX JSON data and parse it
    raw_data = request.get_data()
    parsed = json.loads(raw_data)
    with open(
        os.path.join(current_app.config["CONFIG_FOLDER"], "ontology.json"), "w"
    ) as json_file:
        json_file.write(json.dumps(parsed, indent=4))
    return json.dumps({"success": True}), 200, {"ContentType": "application/json"}
