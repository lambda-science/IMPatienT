import json
import os

import bleach
from flask import (
    current_app,
    redirect,
    render_template,
    request,
    send_from_directory,
    url_for,
)
from jsonschema import validate
from sqlalchemy.orm.attributes import flag_modified

from impatient.app import db
from impatient.app.historeport.onto_func import StandardVocabulary, ImpatientVocab
from impatient.app.histostats.vizualisation import (
    db_to_df,
    table_to_df,
    process_df,
    generate_stat_per,
)
from impatient.app.models import ReportHisto
from impatient.app.ontocreate import bp
from impatient.app.ontocreate.forms import (
    InvertLangButton,
    OntologyDescript,
    OntoUpload,
)


@bp.route("/ontology/<path:filename>")
def onto_json(filename):
    """Route to serve the standard vocabulary JSON file. Used internally by JSTree.

    Args:
        filename (str): Standard vocabulary JSON file name.

    Returns:
        File: returns the file
    """
    return send_from_directory(current_app.config["ONTOLOGY_FOLDER"], filename)


@bp.route("/ontocreate", methods=["GET", "POST"])
def ontocreate():
    """View function for the standard vocabulary creator module.

    Returns:
        str: HTML page for the standard creator module.
    """
    form = OntologyDescript()
    form2 = InvertLangButton()
    form_onto = OntoUpload()
    if form_onto.validate_on_submit() and form_onto.onto_file.data:
        # Get the uploaded file
        uploaded_file = form_onto.onto_file.data
        # Check if the file has an allowed extension
        if uploaded_file.filename[-4:] == "json":
            onto_data = ImpatientVocab()
            onto_data.load_json_f(uploaded_file)

        else:
            onto_data = ImpatientVocab()
            onto_data.load_ontology_f(uploaded_file)
            onto_data.onto_to_json()

        validate(
            instance=onto_data.impatient_json,
            schema=current_app.config["ONTO_SCHEMA"],
        )
        onto_data.impatient_json[0]["data"]["image_annotation"] = True
        file_path = os.path.join(current_app.config["ONTOLOGY_FOLDER"], "ontology.json")
        flag_valid = True

        if flag_valid:
            onto_data.dump_json(file_path)
            for report in ReportHisto.query.all():
                report.ontology_tree = onto_data.impatient_json
                flag_modified(report, "ontology_tree")
            db.session.commit()
            # Update The DashApp Callback & layout
            # By Force reloading the layout code & callbacks
            dashapp = current_app.config["DASHAPP"]
            with current_app.app_context():
                import importlib
                import sys

                importlib.reload(sys.modules["impatient.app.dashapp.callbacks"])
                import impatient.app.dashapp.layout

                importlib.reload(impatient.app.dashapp.layout)
                dashapp.layout = impatient.app.dashapp.layout.layout
            return redirect(url_for("ontocreate.ontocreate"))
    return render_template(
        "ontocreate.html", form=form, form2=form2, form_onto=form_onto
    )


@bp.route("/modify_onto", methods=["PATCH"])
def modify_onto():
    """API PATCH route to update the standard vocabulary JSON file with modifications.
    PATCH AJAX Requestion from JSTree.

    Returns:
        json: JSON response with success code.
    """
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
        sanitized_json = json.loads(bleach.clean(json.dumps(clean_tree)))
        json.dump(sanitized_json, json_file, indent=4)

    # Update All Reports to the latest Version of ontology
    template_ontology = StandardVocabulary(clean_tree)
    for report in ReportHisto.query.all():
        current_report_ontology = StandardVocabulary(report.ontology_tree)
        updated_report_ontology = json.loads(
            bleach.clean(
                json.dumps(current_report_ontology.update_ontology(template_ontology))
            )
        )
        # Issue: SQLAlchemy not updating JSON https://stackoverflow.com/questions/42559434/updates-to-json-field-dont-persist-to-db

        report.ontology_tree = updated_report_ontology
        flag_modified(report, "ontology_tree")
    db.session.commit()

    # Update The DashApp Callback & layout
    # By Force reloading the layout code & callbacks
    dashapp = current_app.config["DASHAPP"]
    with current_app.app_context():
        import importlib
        import sys

        importlib.reload(sys.modules["impatient.app.dashapp.callbacks"])
        import impatient.app.dashapp.layout

        importlib.reload(impatient.app.dashapp.layout)
        dashapp.layout = impatient.app.dashapp.layout.layout
    return json.dumps({"success": True}), 200, {"ContentType": "application/json"}


@bp.route("/download_onto", methods=["GET"])
def download_onto():
    """Route to download the standard vocabulary JSON file.

    Returns:
        File: returns the file
    """
    return send_from_directory(
        current_app.config["ONTOLOGY_FOLDER"], "ontology.json", as_attachment=True
    )


@bp.route("/upload_onto", methods=["POST"])
def upload_onto():
    """Route to upload an ontology in place as JSON, OWL or OBO file."""
    return send_from_directory(
        current_app.config["ONTOLOGY_FOLDER"], "ontology.json", as_attachment=True
    )


@bp.route("/download_onto_as_obo", methods=["GET"])
def download_onto_as_obo():
    """Route to download the standard vocabulary JSON file.

    Returns:
        File: returns the file
    """
    my_onto = ImpatientVocab()
    my_onto.load_json(
        os.path.join(current_app.config["ONTOLOGY_FOLDER"], "ontology.json")
    )
    my_onto.json_to_onto()
    my_onto.dump_onto(
        os.path.join(current_app.config["ONTOLOGY_FOLDER"], "ontology.obo")
    )
    return send_from_directory(
        current_app.config["ONTOLOGY_FOLDER"], "ontology.obo", as_attachment=True
    )


@bp.route("/invert_lang", methods=["POST"])
def invert_lang():
    """API POST route to invert the language of the standard vocabulary JSON file.

    Returns:
        redirect: Refreshes the page to reload the Standard Vocabulary JSON file.
    """

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

    df = db_to_df()
    df, features_col = table_to_df(df, onto)
    df = process_df(df)
    generate_stat_per(df, features_col, onto)

    # Update The DashApp Callback & layout
    # By Force reloading the layout code & callbacks
    dashapp = current_app.config["DASHAPP"]
    with current_app.app_context():
        import importlib
        import sys

        importlib.reload(sys.modules["impatient.app.dashapp.callbacks"])
        import impatient.app.dashapp.layout

        importlib.reload(impatient.app.dashapp.layout)
        dashapp.layout = impatient.app.dashapp.layout.layout

    return redirect(url_for("ontocreate.ontocreate"))
