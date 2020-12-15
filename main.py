import os
import json
import pandas as pd

from flask import Flask, flash, request, redirect, url_for, render_template, send_from_directory, session
from werkzeug.utils import secure_filename
from PIL import Image

from glob import glob
from src import deepzoom

# Constant variable for folders and allowed extension
UPLOAD_FOLDER = "uploads"
REPORT_FOLDER = "results"
ALLOWED_EXTENSIONS = {"tif", "tiff", "png", "jpg", "jpeg"}

# Flask app initialisation and configuration
app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["REPORT_FOLDER"] = REPORT_FOLDER
app.config["SECRET_KEY"] = "myverylongsecretkey"


def allowed_file(filename):
    """Check if the sumbmitted file name is in allowed extension"""
    return "." in filename and \
           filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def create_feature_list(config_file):
    """Extract the list of feature and format them from the configuration file path"""
    feature_df = pd.read_csv(config_file, sep='\t', header=None)
    feature_list = [(row[0].strip().replace(" ", "_"), row[0], row[1])
                    for index, row in feature_df.iterrows()]
    return feature_list


def create_deepzoom_file(image_path):
    """Convert an image to a deep zoom image format. Create .dzi file and a folder with the name of the image"""
    # Specify your source image
    SOURCE = image_path
    # Create Deep Zoom Image creator with weird parameters
    creator = deepzoom.ImageCreator(
        tile_size=256,
        tile_overlap=2,
        tile_format="png",
        image_quality=1,
    )
    # Create Deep Zoom image pyramid from source
    creator.create(SOURCE, "" + image_path + ".dzi")


def create_history_file():
    """List all images with allowed extensions in the upload folder"""
    file_list = [(i.split("/")[-1].split("_")[0], i.split("/")[-1])
                 for i in glob("uploads/*")
                 if i.split(".")[-1] in ALLOWED_EXTENSIONS]
    return file_list


@app.route("/uploads/<path:filename>")
def send_dzi(filename):
    """Serve files located in subfolder inside uploads folder"""
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


@app.route("/uploads/<filename>")
def uploads(filename):
    """Serve files located in uploads folder"""
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
    file_list = create_history_file()
    if request.method == "POST":
        # check if the post request has the file part
        if "file" not in request.files or "patient_ID" not in request.form:
            flash("No file part or patient_ID")
            return redirect(request.url)
        file = request.files["file"]
        patient_ID = request.form["patient_ID"]
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == "":
            flash("No selected file")
            return redirect(request.url)
        if file and allowed_file(file.filename) and patient_ID:
            filename = secure_filename(patient_ID + "_" + file.filename)
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            # Create the deep zoom image and save filename & patient ID from the form
            create_deepzoom_file(UPLOAD_FOLDER + "/" + filename)
            session["filename"] = filename
            session["patient_ID"] = patient_ID
            return redirect(
                url_for("annot_page", filename=filename,
                        patient_ID=patient_ID))
    return render_template("index.html", file_list=file_list)


@app.route("/annot", methods=["GET", "POST"])
def annot_page():
    """Render the annotation page after the upload of the initial image. 
    Redirects to the results page when the annotation form is submitted."""
    filename = request.args.get("filename")
    session["filename"] = request.args.get("filename")
    session["patient_ID"] = request.args.get("patient_ID")
    feature_list = create_feature_list("config/config_ontology.tsv")
    if request.method == "POST":
        if "submit_button" in request.form:
            # When the form is submitted we store the form data in the session variable (cookie) under the "info_annot" key
            data = request.form.to_dict()
            session["info_annot"] = data
            return redirect(url_for("write_report"))
    return render_template("annot.html",
                           filename=filename,
                           thumbnail=filename + "_thumbnail.jpg",
                           feature_list=feature_list,
                           patient_ID=session["patient_ID"])


@app.route("/write_annot", methods=["POST"])
def write_annot():
    """Write new annotation entries (json data) coming from the javascript plugin Annotorious (OpenSeaDragon Plugin) to a file named after the image.
    New annotations data are coming from an AJAX GET Request based on the Anno JS Object (see annot.html)."""
    annot_list = []
    raw_data = request.get_data()
    parsed = json.loads(raw_data)
    # If no annotations yet: json file is created
    if os.path.exists("results/" + session["filename"] + ".json") == False:
        with open("results/" + session["filename"] + ".json",
                  "w") as json_file:
            annot_list.append(parsed)
            json_file.write(json.dumps(annot_list, indent=4))
    # If there are already some annotation: we add the new annotations to the file
    else:
        # First open as read only to load existing JSON
        with open("results/" + session["filename"] + ".json",
                  "r") as json_file:
            old_data = json.load(json_file)
            old_data.append(parsed)
        # Then open as write to overwrite the old file with old json+new data
        with open("results/" + session["filename"] + ".json",
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
    with open("results/" + session["filename"] + ".json", "r") as json_file:
        old_data = json.load(json_file)
        # Compare ID of annotation and replace the old annotations with the new one when there is a match in IDs.
        for anot in old_data:
            if parsed["id"] != anot["id"]:
                updated_list.append(anot)
            elif parsed["id"] == anot["id"]:
                updated_list.append(parsed)
    # Write the new annotations JSON data to file.
    with open("results/" + session["filename"] + ".json", "w") as json_file:
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
    with open("results/" + session["filename"] + ".json", "r") as json_file:
        old_data = json.load(json_file)
        # If annotation ID is different from the ID of deletion command we save them to a list. Matching ID will be skipped and erased.
        for anot in old_data:
            if parsed["id"] != anot["id"]:
                updated_list.append(anot)
    # Write the new annotations JSON data to file.
    with open("results/" + session["filename"] + ".json", "w") as json_file:
        json_file.write(json.dumps(updated_list, indent=4))
    return json.dumps({"success": True}), 200, {
        "ContentType": "application/json"
    }


@app.route("/results", methods=["GET", "POST"])
def write_report():
    """Write the histological report and serve the results page for patient with download links"""
    # Access the Session cookie and pop out basic informations for the file header
    prenom_patient = session["info_annot"].pop("prenom_patient")
    nom_patient = session["info_annot"].pop("nom_patient")
    id_patient = session["patient_ID"]
    redacteur_rapport = session["info_annot"].pop("redacteur_rapport")
    diag = session["info_annot"].pop("diag")
    del session["info_annot"]["submit_button"]
    # Format report and annotation file name
    filename_report = session["filename"] + ".txt"
    filename_annot = session["filename"] + ".json"
    # Write the histology report to file with first the basic informations
    f = open("results/" + filename_report, "w")
    f.write("Prenom_Patient\t" + prenom_patient + "\n")
    f.write("Nom_Patient\t" + nom_patient + "\n")
    f.write("ID_Patient\t" + id_patient + "\n")
    f.write("Redacteur_histo\t" + redacteur_rapport + "\n")
    f.write("Diagnostic\t" + diag + "\n")
    # Then we write each histology feature values with a loop
    for i in session["info_annot"]:
        f.write(i + "\t" + session["info_annot"][i] + "\n")
    # Finally we render the results page
    return render_template("results.html",
                           data=session["info_annot"],
                           prenom_patient=prenom_patient,
                           nom_patient=nom_patient,
                           id_patient=id_patient,
                           redacteur_rapport=redacteur_rapport,
                           filename_report=filename_report,
                           filename_annot=filename_annot)


if __name__ == "__main__":
    # Run the app, access it in the browser at: 127.0.0.1:5010/
    app.run(debug=True, host="127.0.0.1", port=5010)