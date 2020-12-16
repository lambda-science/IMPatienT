import os
import json

from app import app
from app.forms import ImageForm, AnnotForm
import app.histofunc as Histofunc

from flask import Flask, flash, request, redirect, url_for, render_template, send_from_directory, session
from werkzeug.utils import secure_filename


@app.route("/uploads/<path:filename>")
def uploads(filename):
    """Serve files located in subfolder inside uploads folder"""
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


@app.route("/results/<path:filename>")
def get_report(filename):
    """Serve files located in subfolder inside results"""
    return send_from_directory(app.config["REPORT_FOLDER"], filename)


@app.route("/", methods=["GET", "POST"])
@app.route("/index", methods=["GET", "POST"])
def upload_file():
    """Index page that is used to upload the image to the app and register patient ID.
    Redirect to the annotation page after a succesful upload.
    Also show the availiable file that already have been uploaded"""
    file_list = Histofunc.create_history_file()
    form = ImageForm()
    if form.validate_on_submit():
        file = form.image.data
        patient_ID = form.patient_ID.data
        filename = secure_filename(patient_ID + "_" + file.filename)
        file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
        # Create the deep zoom image
        Histofunc.create_deepzoom_file(
            os.path.join(app.config["UPLOAD_FOLDER"], filename))
        return redirect(
            url_for("annot_page", filename=filename, patient_ID=patient_ID))
    return render_template("index.html", file_list=file_list, form=form)


@app.route("/annot", methods=["GET", "POST"])
def annot_page():
    """Render the annotation page after the upload of the initial image. 
    Redirects to the results page when the annotation form is submitted."""
    session["filename"] = request.args.get("filename")
    session["patient_ID"] = request.args.get("patient_ID")
    form = AnnotForm(session["patient_ID"])
    if form.validate_on_submit():
        # Save form data in the session cookie
        session["patient_nom"] = form.patient_nom.data
        session["patient_prenom"] = form.patient_prenom.data
        session["expert_name"] = form.expert_name.data
        session["diagnostic"] = form.diagnostic.data
        session["feature"] = {}
        for feature in app.config["FEATURE_LIST"]:
            session["feature"][feature[0]] = form.data[feature[0]]
        return redirect(url_for("write_report"))
    return render_template("annot.html",
                           filename=session["filename"],
                           feature_list=app.config["FEATURE_LIST"],
                           patient_ID=session["patient_ID"],
                           form=form)


@app.route("/write_annot", methods=["POST"])
def write_annot():
    """Write new annotation entries (json data) coming from the javascript plugin Annotorious (OpenSeaDragon Plugin) to a file named after the image.
    New annotations data are coming from an AJAX GET Request based on the Anno JS Object (see annot.html)."""
    annot_list = []
    raw_data = request.get_data()
    parsed = json.loads(raw_data)
    # If no annotations yet: json file is created
    if os.path.exists("results/" + session["filename"] + ".json") == False:
        with open(os.path.join("results/", session["filename"] + ".json"),
                  "w") as json_file:
            annot_list.append(parsed)
            json_file.write(json.dumps(annot_list, indent=4))
    # If there are already some annotation: we add the new annotations to the file
    else:
        # First open as read only to load existing JSON
        with open(os.path.join("results/", session["filename"] + ".json"),
                  "r") as json_file:
            old_data = json.load(json_file)
            old_data.append(parsed)
        # Then open as write to overwrite the old file with old json+new data
        with open(os.path.join("results/", session["filename"] + ".json"),
                  "w") as json_file:
            json_file.write(json.dumps(old_data, indent=4))
    return json.dumps({"success": True}), 200, {
        "ContentType": "application/json"
    }


@app.route("/update_annot", methods=["POST"])
def update_annot():
    """Update existing annotaions (json data) coming from the javascript plugin Annotorious (OpenSeaDragon Plugin) in the annotation json file named after the image.
    Updated annotations data are coming from an AJAX GET Request based on the Anno JS Object (see annot.html)."""
    raw_data = request.get_data()
    parsed = json.loads(raw_data)
    updated_list = []
    # First open as read only to load existing JSON
    with open(os.path.join("results/", session["filename"] + ".json"),
              "r") as json_file:
        old_data = json.load(json_file)
        # Compare ID of annotation and replace the old annotations with the new one when there is a match in IDs.
        for anot in old_data:
            if parsed["id"] != anot["id"]:
                updated_list.append(anot)
            elif parsed["id"] == anot["id"]:
                updated_list.append(parsed)
    # Write the new annotations JSON data to file.
    with open(os.path.join("results/", session["filename"] + ".json"),
              "w") as json_file:
        json_file.write(json.dumps(updated_list, indent=4))
    return json.dumps({"success": True}), 200, {
        "ContentType": "application/json"
    }


@app.route("/delete_annot", methods=["POST"])
def delete_annot():
    """Delete existing annotaions (json data) if the user delete an annotion of the javascript plugin Annotorious (OpenSeaDragon Plugin).
    Delete command is coming from an AJAX GET Request based on the Anno JS Object (see annot.html)."""
    raw_data = request.get_data()
    parsed = json.loads(raw_data)
    updated_list = []
    # First open as read only to load existing JSON
    with open(os.path.join("results/", session["filename"] + ".json"),
              "r") as json_file:
        old_data = json.load(json_file)
        # If annotation ID is different from the ID of deletion command we save them to a list. Matching ID will be skipped and erased.
        for anot in old_data:
            if parsed["id"] != anot["id"]:
                updated_list.append(anot)
    # Write the new annotations JSON data to file.
    with open(os.path.join("results/", session["filename"] + ".json"),
              "w") as json_file:
        json_file.write(json.dumps(updated_list, indent=4))
    return json.dumps({"success": True}), 200, {
        "ContentType": "application/json"
    }


@app.route("/results", methods=["GET", "POST"])
def write_report():
    """Write the histological report and serve the results page for patient with download links"""
    # Write the histology report to file with first the basic informations
    with open(os.path.join("results/", session["filename"] + ".txt"),
              "w") as f:
        f.write("Prenom_Patient\t" + session["patient_prenom"] + "\n")
        f.write("Nom_Patient\t" + session["patient_nom"] + "\n")
        f.write("ID_Patient\t" + session["patient_ID"] + "\n")
        f.write("Redacteur_histo\t" + session["expert_name"] + "\n")
        f.write("Diagnostic\t" + session["diagnostic"] + "\n")
        # Then we write each histology feature values with a loop
        for i in session["feature"]:
            f.write(i + "\t" + session["feature"][i] + "\n")

    # Finally we render the results page
    return render_template("results.html",
                           feature_info=session["feature"],
                           prenom_patient=session["patient_prenom"],
                           nom_patient=session["patient_nom"],
                           id_patient=session["patient_ID"],
                           redacteur_rapport=session["expert_name"],
                           filename_report=session["filename"] + ".txt",
                           filename_annot=session["filename"] + ".json")