import os
import json

from app import db
from app.ocr import bp
from app.ocr.forms import PdfForm, OcrForm
import app.ocr.ocr as Ocr
from app.models import User, Patient, Pdf

from flask import Flask, flash, request, redirect, url_for, render_template, send_from_directory, current_app
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename
import shutil


@bp.route("/data/<path:filename>")
@login_required
def data_folder(filename):
    """Serve files located in patient subfolder inside folder"""
    pdf_requested = Pdf.query.filter_by(
        pdf_name=filename.split("/")[-1],
        patient_id=filename.split("/")[-1].split("_")[0]).first()
    if pdf_requested != None and pdf_requested.expert_id == current_user.id:
        return send_from_directory(current_app.config["DATA_FOLDER"], filename)
    else:
        return "Unauthorized !", 401


@bp.route("/upload_pdf", methods=["GET", "POST"])
@login_required
def upload_pdf():
    """Index page that is used to upload the PDF to the app and register patient ID.
    Redirect to the OCR results page after a succesful upload.
    Also show the availiable PDF files that already have been uploaded"""
    form = PdfForm()
    # Wipe old temporary data form user
    temp_user_dir = os.path.join(current_app.config["TEMP_FOLDER"],
                                 current_user.username)
    try:
        shutil.rmtree(temp_user_dir)
    except:
        pass

    # Show PDF File History linked to current user
    pdf_history = Pdf.query.filter_by(expert_id=current_user.id)
    if form.validate_on_submit():
        file = form.pdf.data
        patient_ID = form.patient_ID.data
        filename = secure_filename(patient_ID + "_" + file.filename)

        # Create a data folder for patient
        data_patient_dir = os.path.join(current_app.config["DATA_FOLDER"],
                                        patient_ID)
        if not os.path.exists(data_patient_dir):
            os.makedirs(data_patient_dir)

        # Save the PDF to patient data folder
        file.save(os.path.join(data_patient_dir, filename))

        # Create our new PDF & Patient database entry
        pdf = Pdf(pdf_name=filename,
                  patient_id=form.patient_ID.data,
                  expert_id=current_user.id,
                  lang=form.lang.data,
                  pdf_path=os.path.join(data_patient_dir, filename))
        patient = Patient(id=form.patient_ID.data,
                          patient_name=form.patient_nom.data,
                          patient_firstname=form.patient_prenom.data)
        # Check if the image or patient already exist in DB (same filename & patient ID)
        # If not: add it to DB
        if patient.existAlready() == False:
            db.session.add(patient)

        if pdf.isduplicated() == False:
            db.session.add(pdf)

        db.session.commit()

        # Finally redirect to annotation
        return redirect(
            url_for("ocr.ocr_results",
                    filename=filename,
                    patient_ID=patient_ID))
    return render_template("ocr/ocr_upload.html",
                           form=form,
                           pdf_history=pdf_history)


@bp.route("/ocr_results", methods=["GET", "POST"])
@login_required
def ocr_results():
    """Render the OCR results page after the upload of the initial PDF. 
    Render submit PDF and OCR to database button."""
    form = OcrForm()
    # Query the database from arg in get request
    pdf_requested = Pdf.query.filter_by(
        pdf_name=request.args.get("filename"),
        patient_id=request.args.get("patient_ID")).first()

    # If PDF exist and is associated to current user: serve it
    if pdf_requested != None and form.validate_on_submit(
    ) == False and pdf_requested.expert_id == current_user.id:

        rel_filepath = os.path.join("data", request.args.get("patient_ID"),
                                    pdf_requested.pdf_name)
        # Perform OCR on the PDF file
        ocr_text_list = Ocr.pdf_to_text(pdf_requested.pdf_path,
                                        pdf_requested.lang)
        # Join per page text with NEW PAGE tag between elements
        ocr_text = '\n##### NEW PAGE #####\n'.join(ocr_text_list)
        form.ocr_text.data = ocr_text

    elif pdf_requested != None and form.validate_on_submit(
    ) == True and pdf_requested.expert_id == current_user.id:
        pdf_requested.ocr_text = form.ocr_text.data
        db.session.commit()
        return redirect(url_for('ocr.upload_pdf'))

    # Error handling
    elif pdf_requested == None:
        flash('PDF doesn\'t exist!', "error")
        return redirect(url_for('ocr.upload_pdf'))
    elif pdf_requested.expert_id != current_user.id:
        flash('User not authorized for this PDF!', "error")
        return redirect(url_for('ocr.upload_pdf'))
    return render_template("ocr/ocr_results.html",
                           form=form,
                           ocr_text=ocr_text,
                           patient_ID=request.args.get("patient_ID"),
                           rel_filepath=rel_filepath)


@bp.route("/delete_pdf", methods=["DELETE"])
@login_required
def delete_pdf():
    """Page to delete an PDF record from database from AJAX request"""
    # Get AJAX JSON data and parse it
    raw_data = request.get_data()
    parsed = json.loads(raw_data)
    pdf_requested = Pdf.query.filter_by(
        pdf_name=parsed["pdf_name"], patient_id=parsed["patient_id"]).first()
    # If current user is the creator of PDF: delete from DB
    if pdf_requested != None and pdf_requested.expert_id == current_user.id:
        db.session.delete(pdf_requested)
        db.session.commit()
        return json.dumps({"success": True}), 200, {
            "ContentType": "application/json"
        }
    # Error message if not the right user for given PDF
    else:
        flash('Unautorized database manipulation (delete_pdf)', "error")
        return redirect(url_for('ocr.upload_file'))