import os
import json
import pandas as pd

from flask import Flask, flash, request, redirect, url_for, render_template, send_from_directory, session
from werkzeug.utils import secure_filename
from PIL import Image

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, PasswordField, BooleanField, SubmitField, RadioField
from wtforms.validators import DataRequired, Required

from glob import glob
from src import deepzoom

# Constant variable for folders and allowed extension
UPLOAD_FOLDER = "uploads"
REPORT_FOLDER = "results"
ALLOWED_EXTENSIONS = ["tif", "tiff", "png", "jpg", "jpeg"]

# Flask app initialisation and configuration
app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["REPORT_FOLDER"] = REPORT_FOLDER
app.config["SECRET_KEY"] = "myverylongsecretkey"


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
    class ImageForm(FlaskForm):
        image = FileField(validators=[
            FileRequired(),
            FileAllowed(ALLOWED_EXTENSIONS,
                        "Ce fichier n'est pas une image valide !")
        ],
                          render_kw={"class": "form-control-file"})
        patient_ID = StringField('patient_ID',
                                 validators=[DataRequired()],
                                 render_kw={
                                     "placeholder": "Identifiant Patient",
                                     "class": "form-control"
                                 })
        submit = SubmitField('Upload',
                             render_kw={"class": "btn btn-primary mb-2"})

    file_list = create_history_file()
    form = ImageForm()
    if form.validate_on_submit():
        file = form.image.data
        patient_ID = form.patient_ID.data
        filename = secure_filename(patient_ID + "_" + file.filename)
        file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
        # Create the deep zoom image
        create_deepzoom_file(
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
    feature_list = create_feature_list(
        os.path.join("config", "config_ontology.tsv"))

    class AnnotForm(FlaskForm):
        patient_nom = StringField('patient_nom',
                                  validators=[DataRequired()],
                                  render_kw={
                                      "placeholder": "Nom Patient",
                                      "class": "form-control"
                                  })
        patient_prenom = StringField('patient_prenom',
                                     validators=[DataRequired()],
                                     render_kw={
                                         "placeholder": "Prénom Patient",
                                         "class": "form-control"
                                     })
        patient_id = StringField('patient_ID',
                                 render_kw={
                                     "placeholder": session["patient_ID"],
                                     "class": "form-control",
                                     "readonly": "True"
                                 })
        expert_name = StringField('expert_name',
                                  validators=[DataRequired()],
                                  render_kw={
                                      "placeholder": "Nom du rapporteur",
                                      "class": "form-control",
                                  })
        submit = SubmitField('Générer le rapport',
                             render_kw={"class": "btn btn-primary mb-2"})

        diagnostic = StringField('diagnostic',
                                 validators=[DataRequired()],
                                 render_kw={
                                     "placeholder": "Diagnostique de Maladie",
                                     "class": "form-control"
                                 })

    for feature in feature_list:
        setattr(
            AnnotForm, feature[0],
            RadioField(feature[1],
                       choices=[('1', 'Présent'), ('-1', 'Absent'),
                                ('0', 'Incertain')],
                       default='-1',
                       validators=[DataRequired()]))
    form = AnnotForm()
    if form.validate_on_submit():
        # Save form data in the session cookie
        session["patient_nom"] = form.patient_nom.data
        session["patient_prenom"] = form.patient_prenom.data
        session["expert_name"] = form.expert_name.data
        session["diagnostic"] = form.diagnostic.data
        session["feature"] = {}
        for feature in feature_list:
            session["feature"][feature[0]] = form.data[feature[0]]
        return redirect(url_for("write_report"))
    return render_template("annot.html",
                           filename=session["filename"],
                           feature_list=feature_list,
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


if __name__ == "__main__":
    # Run the app, access it in the browser at: 127.0.0.1:5010/
    app.run(debug=True, host="127.0.0.1", port=5010)