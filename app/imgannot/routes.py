import os
import json
import subprocess
import shutil

from flask import flash, request, redirect, url_for, render_template
from flask import send_from_directory, session, current_app
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename

from app import db
from app.imgannot import bp
from app.imgannot.forms import ImageForm, AnnotForm, DeleteButton
from app.models import Image, Patient
import app.imgannot.histo as Histo


@bp.route("/temp/<path:filename>")
@login_required
def temp(filename):
    """Serve files located in subfolder inside temp folder"""
    return send_from_directory(current_app.config["TEMP_FOLDER"], filename)


@bp.route("/data/<path:filename>")
@login_required
def data_folder(filename):
    """Serve files located in patient subfolder inside folder"""
    return send_from_directory(current_app.config["DATA_FOLDER"], filename)


@bp.route("/upload_img", methods=["GET", "POST"])
@login_required
def upload_file():
    """Image upload page that is used to upload the image to the app and register patient ID & name
    Redirect to the annotation page after a succesful upload.
    Also show the image stored in DB for current user"""
    form = ImageForm()
    delete_button = DeleteButton()

    # Show Image History
    image_history = Image.query.all()

    if form.validate_on_submit():
        file = form.image.data
        patient_id = form.patient_ID.data
        filename = secure_filename(patient_id + "_" + file.filename)

        # Create a data folder for patient
        data_patient_dir = os.path.join(current_app.config["DATA_FOLDER"],
                                        patient_id)
        if not os.path.exists(data_patient_dir):
            os.makedirs(data_patient_dir)
        # Save the image to patient data folder
        file.save(os.path.join(data_patient_dir, filename))

        # Create our new Image & Patient database entry
        image = Image(image_name=filename,
                      patient_id=form.patient_ID.data,
                      expert_id=current_user.id,
                      image_path=os.path.join(data_patient_dir, filename))
        patient = Patient(id=form.patient_ID.data,
                          patient_name=form.patient_nom.data,
                          patient_firstname=form.patient_prenom.data)
        # Check if the image or patient already exist in DB (same filename & patient ID)
        # If not: add it to DB
        if not patient.exist_already():
            db.session.add(patient)

        if not image.isduplicated():
            db.session.add(image)

        db.session.commit()

        # Finally redirect to annotation
        return redirect(url_for("imgannot.annot_page", id=image.id))
    return render_template("imgannot/upload_img.html",
                           form=form,
                           delete_button=delete_button,
                           image_history=image_history)


@bp.route('/delete_img/<id_img>', methods=['POST'])
@login_required
def delete_img(id_img):
    """Page delete a histology report from database with delete button."""
    form = DeleteButton()
    # Retrieve database entry and delete it if existing
    if form.validate_on_submit():
        image = Image.query.get(id_img)
        if image is None:
            flash('Image {} not found.'.format(id_img), "danger")
            return redirect(url_for('imgannot.upload_file'))
        db.session.delete(image)
        db.session.commit()
        flash('Deleted Image entry {}!'.format(id_img), "success")
        return redirect(url_for('imgannot.upload_file'))
    else:
        return redirect(url_for('imgannot.upload_file'))


@bp.route("/annot", methods=["GET", "POST"])
@login_required
def annot_page():
    """Image annotation page with form.
    Redirects to the results page when the annotation form is submitted."""
    tag_list = [i[1] for i in current_app.config["FEATURE_LIST"]]
    feature_list = current_app.config["FEATURE_LIST"]

    # Query the database from args data
    image_requested = Image.query.get(request.args.get("id"))

    # Prefill the feature form if already in DB and create feature form field
    if image_requested is not None:
        Histo.generate_feature_form(AnnotForm, image_requested.report_text,
                                    feature_list)
        form = AnnotForm()

    # Create temporary directory name
    temp_user_dir = os.path.join(current_app.config["TEMP_FOLDER"],
                                 current_user.username)

    # If image exist and is associated to current user: serve it
    if image_requested is not None and not form.validate_on_submit():
        # Filename to session for modify annot function.
        session["filename"] = image_requested.image_name
        # Create temporary directory
        if not os.path.exists(temp_user_dir):
            os.makedirs(temp_user_dir)
        # Create the deep zoom image using deepzoom command (subprocess)
        basename = os.path.splitext(
            os.path.basename(image_requested.image_path))[0]
        process = subprocess.Popen([
            "venv/bin/python3", "app/src/deepzoom.py",
            image_requested.image_path, basename, "--output",
            os.path.join(current_app.config["DATA_FOLDER"],
                         image_requested.patient_id, basename)
        ],
                                   stdout=subprocess.PIPE)
        process.wait()
        annot_temp_path = os.path.join(current_user.username,
                                       image_requested.image_name)
        deepzoom_path = os.path.join(image_requested.patient_id, basename)
        # Create the JSON File for annotation from data stored in DB
        with open(
                os.path.join(temp_user_dir,
                             image_requested.image_name + ".json"),
                "w") as json_file:
            annotation_data = json.loads(
                json.dumps(image_requested.annotation_json))

            json_file.write(json.dumps(annotation_data, indent=4))

    # Error handling.
    elif image_requested is None:
        flash('Image doesn\'t exist!', "error")
        return redirect(url_for('imgannot.upload_file'))

    # Once annotation is finished and validated: update DB entry
    if form.validate_on_submit():
        # Extract feature info from form
        feature_form_list = {}
        for feature in current_app.config["FEATURE_LIST"]:
            feature_form_list[feature[0]] = form.data[feature[0]]
        # Write each histology feature values with a loop in a string
        report_string = ""
        for i in feature_form_list:
            report_string = report_string + i + "\t" + feature_form_list[
                i] + "\n"
        # Attach form data to DB entry
        image_requested.report_text = str(report_string)
        image_requested.diagnostic = form.diagnostic.data
        image_requested.age_at_biopsy = form.age_histo.data
        image_requested.type_coloration = form.type_coloration.data

        # Load annotation json file and attach it to DB entry
        with open(
                os.path.join(temp_user_dir,
                             image_requested.image_name + ".json"),
                "r") as json_file:
            data_annot = json.load(json_file)
            image_requested.annotation_json = data_annot
            # Commit new DB entry
            db.session.commit()
        shutil.rmtree(temp_user_dir)
        return redirect(url_for("imgannot.upload_file"))
    return render_template("imgannot/annot.html",
                           deepzoom_path=deepzoom_path,
                           annot_temp_path=annot_temp_path,
                           feature_list=current_app.config["FEATURE_LIST"],
                           form=form,
                           tag_list=str(tag_list))


@bp.route("/modify_annot", methods=["POST", "PATCH", "DELETE"])
@login_required
def modify_annot():
    """Write/Update/Delete existing annotations (json data) according to
    JS Plugin Annotorious AJAX Request.
    Command is coming from an AJAX Request based on the Anno JS Object
    (see annot.html). (POST/PATCH/DELETE)"""

    # Create temporary directory name
    temp_user_dir = os.path.join(current_app.config["TEMP_FOLDER"],
                                 current_user.username)
    annot_list = []
    updated_list = []
    # Get AJAX JSON data and parse it
    raw_data = request.get_data()
    parsed = json.loads(raw_data)
    # If no annotations yet: json file is created
    if not os.path.exists(
            os.path.join(temp_user_dir, session["filename"] + ".json")):
        with open(os.path.join(temp_user_dir, session["filename"] + ".json"),
                  "w") as json_file:
            annot_list.append(parsed)
            json_file.write(json.dumps(annot_list, indent=4))
    # If there are already some annotation: we write/delete/update depending on request type
    else:
        # First open as read only to load existing JSON
        with open(os.path.join(temp_user_dir, session["filename"] + ".json"),
                  "r") as json_file:
            old_data = json.load(json_file)
            if request.method == 'POST':
                old_data.append(parsed)
                updated_list = old_data
            elif request.method == 'PATCH':
                # Compare ID of annotation and replace the old annotations
                # with the new one when there is a match in IDs.
                for anot in old_data:
                    if parsed["id"] != anot["id"]:
                        updated_list.append(anot)
                    elif parsed["id"] == anot["id"]:
                        updated_list.append(parsed)
            elif request.method == 'DELETE':
                # If annotation ID is different from the ID of deletion
                # command we save them to a list. Matching ID will be
                # skipped and erased.
                for anot in old_data:
                    if parsed["id"] != anot["id"]:
                        updated_list.append(anot)
        with open(os.path.join(temp_user_dir, session["filename"] + ".json"),
                  "w") as json_file:
            json_file.write(json.dumps(updated_list, indent=4))
    return json.dumps({"success": True}), 200, {
        "ContentType": "application/json"
    }
