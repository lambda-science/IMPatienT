from app import db
from app.orthocreate import bp
from app.orthocreate.forms import OntologyDescript

import os
import json
from flask import Flask, render_template, session, current_app, send_from_directory, request
from flask_login import current_user, login_required


@bp.route("/config/<path:filename>")
@login_required
def onto_json(filename):
    """Serve files located in patient subfolder inside folder"""
    return send_from_directory(current_app.config["CONFIG_FOLDER"], filename)


@bp.route("/orthocreate", methods=["GET", "POST"])
@login_required
def orthocreate():
    """palceholder"""
    form = OntologyDescript()
    if form.validate_on_submit():
        print(form.data)
    return render_template("orthocreate/orthocreate.html", form=form)


@bp.route("/modify_ontho", methods=["PATCH"])
@login_required
def modify_ontho():
    """Update ontology json file with PATCH Ajax Request from JSTree"""
    # Get AJAX JSON data and parse it
    raw_data = request.get_data()
    parsed = json.loads(raw_data)
    with open(
            os.path.join(current_app.config["CONFIG_FOLDER"], "ontology.json"),
            "w") as json_file:
        json_file.write(json.dumps(parsed, indent=4))
    return json.dumps({"success": True}), 200, {
        "ContentType": "application/json"
    }