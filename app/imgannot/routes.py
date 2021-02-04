import os
import json

from app import db
from app.imgannot import bp
from app.imgannot.forms import ImageForm, AnnotForm
import app.imgannot.histo as Histo
from app.models import User, Image, Patient

from flask import Flask, flash, request, redirect, url_for, render_template, send_from_directory, session, current_app
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename
import shutil


@bp.route("/temp/<path:filename>")
@login_required
def temp(filename):
    """Serve files located in subfolder inside temp folder"""
    return send_from_directory(current_app.config["TEMP_FOLDER"], filename)


@bp.route("/upload_img", methods=["GET", "POST"])
@login_required
def upload_file():
    """Image upload page that is used to upload the image to the app and register patient ID & name
    Redirect to the annotation page after a succesful upload.
    Also show the image stored in DB for current user"""
    form = ImageForm()
    # Wipe old temporary data form user
    temp_user_dir = os.path.join(current_app.config["TEMP_FOLDER"],
                                 current_user.username)
    try:
        shutil.rmtree(temp_user_dir)
    except:
        pass
    # Show Image History
    image_history = Image.query.filter_by(expert_id=current_user.id)
    if form.validate_on_submit():
        file = form.image.data
        patient_ID = form.patient_ID.data
        filename = secure_filename(patient_ID + "_" + file.filename)

        # Create a data folder for patient
        data_patient_dir = os.path.join(current_app.config["DATA_FOLDER"],
                                        patient_ID)
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
        if patient.existAlready() == False:
            db.session.add(patient)

        if image.isduplicated() == False:
            db.session.add(image)

        db.session.commit()

        # Finally redirect to annotation
        return redirect(
            url_for("imgannot.annot_page",
                    filename=filename,
                    patient_ID=patient_ID))
    return render_template("imgannot/upload_img.html",
                           form=form,
                           image_history=image_history)


# To change to form insead of simple get
@bp.route("/delete_image", methods=["DELETE"])
@login_required
def delete_image():
    """Page to delete an image record from database from AJAX request"""
    # Get AJAX JSON data and parse it
    raw_data = request.get_data()
    parsed = json.loads(raw_data)
    image_requested = Image.query.filter_by(
        image_name=parsed["image_name"],
        patient_id=parsed["patient_id"]).first()
    # If current user is the creator of image: delete from DB
    if image_requested != None and image_requested.expert_id == current_user.id:
        db.session.delete(image_requested)
        db.session.commit()
        return json.dumps({"success": True}), 200, {
            "ContentType": "application/json"
        }
    # Error message if not the right user for given image
    else:
        flash('Unautorized database manipulation (delete_image)', "error")
        return redirect(url_for('imgannot.upload_file'))


@bp.route("/annot", methods=["GET", "POST"])
@login_required
def annot_page():
    """Image annotation page with form.
    Redirects to the results page when the annotation form is submitted."""
    form = AnnotForm()
    tag_list = [i[1] for i in current_app.config["FEATURE_LIST"]]
    # Get the filename of image and patient ID from args.
    session["filename"] = request.args.get("filename")
    session["patient_ID"] = request.args.get("patient_ID")
    # Query the database from args data
    image_requested = Image.query.filter_by(
        image_name=request.args.get("filename"),
        patient_id=request.args.get("patient_ID")).first()
    # If image exist and is associated to current user: serve it
    if image_requested != None and form.validate_on_submit(
    ) == False and image_requested.expert_id == current_user.id:
        session["image_expert_id"] = image_requested.expert_id
        # Create a temporary folder for username
        temp_user_dir = os.path.join(current_app.config["TEMP_FOLDER"],
                                     current_user.username)
        if not os.path.exists(temp_user_dir):
            os.makedirs(temp_user_dir)
        # Create the deep zoom image.

        Histo.create_deepzoom_file(
            image_requested.image_path,
            os.path.join(current_app.config["TEMP_FOLDER"],
                         current_user.username, image_requested.image_name))
        session["filepath"] = os.path.join(current_user.username,
                                           image_requested.image_name)

        # Create the JSON File for annotation from data stored in DB
        with open(os.path.join(temp_user_dir, session["filename"] + ".json"),
                  "w") as json_file:
            annotation_data = json.loads(
                json.dumps(image_requested.annotation_json))

            json_file.write(json.dumps(annotation_data, indent=4))
    # Error handling if no image or not the right user.
    elif image_requested == None:
        flash('Image doesn\'t exist!', "error")
        return redirect(url_for('imgannot.upload_file'))
    elif image_requested.expert_id != current_user.id:
        flash('User not authorized for this image!', "error")
        return redirect(url_for('imgannot.upload_file'))
    # Once annotation is finished and validated: form data in the session cookie
    if form.validate_on_submit():
        session["patient_nom"] = Patient.query.get(
            image_requested.patient_id).patient_name
        session["patient_prenom"] = Patient.query.get(
            image_requested.patient_id).patient_firstname
        session["expert_name"] = image_requested.expert_id
        session["diagnostic"] = form.diagnostic.data
        session["feature"] = {}
        for feature in current_app.config["FEATURE_LIST"]:
            session["feature"][feature[0]] = form.data[feature[0]]
        return redirect(url_for("imgannot.write_report"))
    return render_template("imgannot/annot.html",
                           filename=session["filepath"],
                           feature_list=current_app.config["FEATURE_LIST"],
                           patient_ID=session["patient_ID"],
                           form=form,
                           tag_list=str(tag_list))


@bp.route("/modify_annot", methods=["POST", "PATCH", "DELETE"])
@login_required
def modify_annot():
    """Write/Update/Delete existing annotations (json data) according to JS Plugin Annotorious AJAX Request.
    Command is coming from an AJAX Request based on the Anno JS Object (see annot.html). (POST/PATCH/DELETE)"""
    temp_user_dir = os.path.join(current_app.config["TEMP_FOLDER"],
                                 current_user.username)
    annot_list = []
    updated_list = []
    # Get AJAX JSON data and parse it
    raw_data = request.get_data()
    parsed = json.loads(raw_data)
    # If current user is the creator of image: proceed
    if session["image_expert_id"] == current_user.id:
        # If no annotations yet: json file is created
        if os.path.exists(
                os.path.join(temp_user_dir,
                             session["filename"] + ".json")) == False:
            with open(
                    os.path.join(temp_user_dir, session["filename"] + ".json"),
                    "w") as json_file:
                annot_list.append(parsed)
                json_file.write(json.dumps(annot_list, indent=4))
        # If there are already some annotation: we write/delete/update depending on request type
        else:
            # First open as read only to load existing JSON
            with open(
                    os.path.join(temp_user_dir, session["filename"] + ".json"),
                    "r") as json_file:
                old_data = json.load(json_file)
                if request.method == 'POST':
                    old_data.append(parsed)
                    updated_list = old_data
                elif request.method == 'PATCH':
                    # Compare ID of annotation and replace the old annotations with the new one when there is a match in IDs.
                    for anot in old_data:
                        if parsed["id"] != anot["id"]:
                            updated_list.append(anot)
                        elif parsed["id"] == anot["id"]:
                            updated_list.append(parsed)
                elif request.method == 'DELETE':
                    # If annotation ID is different from the ID of deletion command we save them to a list. Matching ID will be skipped and erased.
                    for anot in old_data:
                        if parsed["id"] != anot["id"]:
                            updated_list.append(anot)
            with open(
                    os.path.join(temp_user_dir, session["filename"] + ".json"),
                    "w") as json_file:
                json_file.write(json.dumps(updated_list, indent=4))
        return json.dumps({"success": True}), 200, {
            "ContentType": "application/json"
        }
    # Error message if not the right user for given image
    else:
        flash('Unautorized database manipulation (write_annot)', "error")
        return redirect(url_for('imgannot.upload_file'))


@bp.route("/results", methods=["GET", "POST"])
@login_required
def write_report():
    """Write the histological report & annotation to DB"""
    temp_user_dir = os.path.join(current_app.config["TEMP_FOLDER"],
                                 current_user.username)
    # Get Image entry from DB to register annotation
    image_requested = Image.query.filter_by(
        image_name=session["filename"],
        patient_id=session["patient_ID"]).first()
    # If Image exist: build the histology text report from session cookie data
    if image_requested != None:
        # Write general patient informations
        report_string = "Prenom_Patient\t" + session["patient_prenom"] + "\n"
        report_string = report_string + "Nom_Patient\t" + session[
            "patient_nom"] + "\n"
        report_string = report_string + "ID_Patient\t" + session[
            "patient_ID"] + "\n"
        report_string = report_string + "Redacteur_histo\t" + str(
            session["expert_name"]) + "\n"
        report_string = report_string + "Diagnostic\t" + session[
            "diagnostic"] + "\n"
        # Then write each histology feature values with a loop
        for i in session["feature"]:
            report_string = report_string + i + "\t" + session["feature"][
                i] + "\n"
        # Attach report_string to DB entry and diagnostic to DB entry
        image_requested.report_text = str(report_string)
        image_requested.diagnostic = session["diagnostic"]
        # Load annotation json file and attach it to DB entry
        with open(os.path.join(temp_user_dir, session["filename"] + ".json"),
                  "r") as json_file:
            data_annot = json.load(json_file)
            image_requested.annotation_json = data_annot
            # Commit new DB entry
            db.session.commit()
        shutil.rmtree(temp_user_dir)
    # Finally we render the results page
    return render_template("imgannot/results.html")
