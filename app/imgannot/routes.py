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
def temp(filename):
    """Serve files located in subfolder inside temp folder"""
    return send_from_directory(current_app.config["UPLOAD_FOLDER"], filename)


@bp.route("/upload_img", methods=["GET", "POST"])
@login_required
def upload_file():
    """Image upload page that is used to upload the image to the app and register patient ID.
    Redirect to the annotation page after a succesful upload.
    Also show the availiable file that already have been uploaded"""
    form = ImageForm()
    # Wipe old temporary data form user
    temp_user_dir = os.path.join(current_app.config["UPLOAD_FOLDER"],
                                 session["username"])
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

        # Create a temporary folder for username

        if not os.path.exists(temp_user_dir):
            os.makedirs(temp_user_dir)
        # Save the image to a temp folder
        file.save(os.path.join(temp_user_dir, filename))
        # Get User ID
        expert = User.query.filter_by(username=session["username"]).first()
        # Create our new Image & Patient database entry
        image = Image(image_name=filename,
                      patient_id=form.patient_ID.data,
                      expert_id=expert.id)
        patient = Patient(id=form.patient_ID.data,
                          patient_name=form.patient_nom.data,
                          patient_firstname=form.patient_prenom.data)
        # Check if the image or patient already exist in DB (same filename & patient ID)
        # If not: add it to DB
        if image.isduplicated() == False:
            image.set_imageblob(os.path.join(temp_user_dir, filename))
            db.session.add(image)
            db.session.commit()

        if patient.existAlready() == False:
            db.session.add(patient)
            db.session.commit()

        # Finally delete the image file in temps folder and redirect to annotation
        if os.path.exists(os.path.join(temp_user_dir, filename)):
            os.remove(os.path.join(temp_user_dir, filename))
        return redirect(
            url_for("imgannot.annot_page",
                    filename=filename,
                    patient_ID=patient_ID))
    return render_template("imgannot/upload_img.html",
                           form=form,
                           image_history=image_history)


# To change to form insead of simple get
@bp.route("/delete_image", methods=["GET", "POST"])
@login_required
def delete_image():
    image_requested = Image.query.filter_by(
        image_name=request.args.get("filename"),
        patient_id=request.args.get("patient_ID")).first()
    if image_requested != None and image_requested.expert_id == current_user.id:
        db.session.delete(image_requested)
        db.session.commit()
    return redirect(url_for('imgannot.upload_file'))


@bp.route("/annot", methods=["GET", "POST"])
@login_required
def annot_page():
    """Render the annotation page after the upload of the initial image. 
    Redirects to the results page when the annotation form is submitted."""
    form = AnnotForm()
    session["filename"] = request.args.get("filename")
    session["patient_ID"] = request.args.get("patient_ID")
    image_requested = Image.query.filter_by(
        image_name=session["filename"],
        patient_id=session["patient_ID"]).first()
    if image_requested != None and form.validate_on_submit(
    ) == False and image_requested.expert_id == current_user.id:
        session["image_expert_id"] = image_requested.expert_id
        # Create a temporary folder for username
        temp_user_dir = os.path.join(current_app.config["UPLOAD_FOLDER"],
                                     session["username"])
        if not os.path.exists(temp_user_dir):
            os.makedirs(temp_user_dir)
        # Create the deep zoom image
        filepath_to_write = os.path.join(temp_user_dir,
                                         image_requested.image_name)
        Histo.write_file(image_requested.image_binary, filepath_to_write)
        Histo.create_deepzoom_file(filepath_to_write)
        session["filepath"] = os.path.join(session["username"],
                                           image_requested.image_name)

        # Create the JSON File for annotation from data stored in DB
        with open(os.path.join(temp_user_dir, session["filename"] + ".json"),
                  "w") as json_file:
            annotation_data = json.loads(
                image_requested.annotation_json.replace("'", '"'))
            json_file.write(json.dumps(annotation_data, indent=4))
    elif image_requested == None:
        flash('Image doesn\'t exist!', "error")
        return redirect(url_for('imgannot.upload_file'))
    elif image_requested.expert_id != current_user.id:
        flash('User not authorized for this image!', "error")
        return redirect(url_for('imgannot.upload_file'))

    if form.validate_on_submit():
        # Save form data in the session cookie
        session["patient_nom"] = "Placeholder"
        session["patient_prenom"] = "Placeholder"
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
                           form=form)


@bp.route("/write_annot", methods=["POST"])
def write_annot():
    """Write new annotation entries (json data) coming from the javascript plugin Annotorious (OpenSeaDragon Plugin) to a file named after the image.
    New annotations data are coming from an AJAX GET Request based on the Anno JS Object (see annot.html)."""
    temp_user_dir = os.path.join(current_app.config["UPLOAD_FOLDER"],
                                 session["username"])
    annot_list = []
    raw_data = request.get_data()
    parsed = json.loads(raw_data)
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
        # If there are already some annotation: we add the new annotations to the file
        else:
            # First open as read only to load existing JSON
            with open(
                    os.path.join(temp_user_dir, session["filename"] + ".json"),
                    "r") as json_file:
                old_data = json.load(json_file)
                old_data.append(parsed)
            # Then open as write to overwrite the old file with old json+new data
            with open(
                    os.path.join(temp_user_dir, session["filename"] + ".json"),
                    "w") as json_file:
                json_file.write(json.dumps(old_data, indent=4))
        return json.dumps({"success": True}), 200, {
            "ContentType": "application/json"
        }
    else:
        flash('Unautorized database manipulation (write_annot)', "error")
        return redirect(url_for('imgannot.upload_file'))


@bp.route("/update_annot", methods=["POST"])
def update_annot():
    """Update existing annotaions (json data) coming from the javascript plugin Annotorious (OpenSeaDragon Plugin) in the annotation json file named after the image.
    Updated annotations data are coming from an AJAX GET Request based on the Anno JS Object (see annot.html)."""
    temp_user_dir = os.path.join(current_app.config["UPLOAD_FOLDER"],
                                 session["username"])
    raw_data = request.get_data()
    parsed = json.loads(raw_data)
    updated_list = []
    if session["image_expert_id"] == current_user.id:
        # First open as read only to load existing JSON
        with open(os.path.join(temp_user_dir, session["filename"] + ".json"),
                  "r") as json_file:
            old_data = json.load(json_file)
            # Compare ID of annotation and replace the old annotations with the new one when there is a match in IDs.
            for anot in old_data:
                if parsed["id"] != anot["id"]:
                    updated_list.append(anot)
                elif parsed["id"] == anot["id"]:
                    updated_list.append(parsed)
        # Write the new annotations JSON data to file.
        with open(os.path.join(temp_user_dir, session["filename"] + ".json"),
                  "w") as json_file:
            json_file.write(json.dumps(updated_list, indent=4))
        return json.dumps({"success": True}), 200, {
            "ContentType": "application/json"
        }
    else:
        flash('Unautorized database manipulation (write_annot)', "error")
        return redirect(url_for('imgannot.upload_file'))


@bp.route("/delete_annot", methods=["POST"])
def delete_annot():
    """Delete existing annotaions (json data) if the user delete an annotion of the javascript plugin Annotorious (OpenSeaDragon Plugin).
    Delete command is coming from an AJAX GET Request based on the Anno JS Object (see annot.html)."""
    temp_user_dir = os.path.join(current_app.config["UPLOAD_FOLDER"],
                                 session["username"])
    raw_data = request.get_data()
    parsed = json.loads(raw_data)
    updated_list = []
    if session["image_expert_id"] == current_user.id:
        # First open as read only to load existing JSON
        with open(os.path.join(temp_user_dir, session["filename"] + ".json"),
                  "r") as json_file:
            old_data = json.load(json_file)
            # If annotation ID is different from the ID of deletion command we save them to a list. Matching ID will be skipped and erased.
            for anot in old_data:
                if parsed["id"] != anot["id"]:
                    updated_list.append(anot)
        # Write the new annotations JSON data to file.
        with open(os.path.join(temp_user_dir, session["filename"] + ".json"),
                  "w") as json_file:
            json_file.write(json.dumps(updated_list, indent=4))
        return json.dumps({"success": True}), 200, {
            "ContentType": "application/json"
        }
    else:
        flash('Unautorized database manipulation (write_annot)', "error")
        return redirect(url_for('imgannot.upload_file'))


@bp.route("/results", methods=["GET", "POST"])
def write_report():
    """Write the histological report and serve the results page for patient with download links"""
    # Write the histology report to file with first the basic informations
    temp_user_dir = os.path.join(current_app.config["UPLOAD_FOLDER"],
                                 session["username"])
    image_requested = Image.query.filter_by(
        image_name=session["filename"],
        patient_id=session["patient_ID"]).first()
    if image_requested != None:
        report_string = "Prenom_Patient\t" + session["patient_prenom"] + "\n"
        report_string = report_string + "Nom_Patient\t" + session[
            "patient_nom"] + "\n"
        report_string = report_string + "ID_Patient\t" + session[
            "patient_ID"] + "\n"
        report_string = report_string + "Redacteur_histo\t" + str(
            session["expert_name"]) + "\n"
        report_string = report_string + "Diagnostic\t" + session[
            "diagnostic"] + "\n"
        # Then we write each histology feature values with a loop
        for i in session["feature"]:
            report_string = report_string + i + "\t" + session["feature"][
                i] + "\n"
        image_requested.report_text = str(report_string)
        image_requested.diagnostic = session["diagnostic"]

        with open(os.path.join(temp_user_dir, session["filename"] + ".json"),
                  "r") as json_file:
            data_annot = json.load(json_file)
            image_requested.annotation_json = str(data_annot)
            db.session.commit()
        shutil.rmtree(temp_user_dir)
    # Finally we render the results page
    return render_template("imgannot/results.html")
