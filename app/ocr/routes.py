import os

from app import db
from app.ocr import bp
from app.ocr.forms import PdfForm, OcrForm
import app.ocr.ocr as Ocr
from app.models import User, Patient, Pdf

from flask import Flask, flash, request, redirect, url_for, render_template, send_from_directory, session, current_app
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename
import shutil


@bp.route("/temp/<path:filename>")
def temp(filename):
    """Serve files located in subfolder inside temp folder"""
    return send_from_directory(current_app.config["UPLOAD_FOLDER"], filename)


@bp.route("/upload_pdf", methods=["GET", "POST"])
@login_required
def upload_pdf():
    """Index page that is used to upload the image to the app and register patient ID.
    Redirect to the annotation page after a succesful upload.
    Also show the availiable file that already have been uploaded"""
    form = PdfForm()
    # Wipe old temporary data form user
    temp_user_dir = os.path.join(current_app.config["UPLOAD_FOLDER"],
                                 session["username"])
    try:
        shutil.rmtree(temp_user_dir)
    except:
        pass
    # Show  History
    pdf_history = Pdf.query.filter_by(expert_id=current_user.id)
    if form.validate_on_submit():
        file = form.pdf.data
        patient_ID = form.patient_ID.data
        filename = secure_filename(patient_ID + "_" + file.filename)

        # Create a temporary folder for username

        if not os.path.exists(temp_user_dir):
            os.makedirs(temp_user_dir)
        # Save the image to a temp folder
        file.save(os.path.join(temp_user_dir, filename))
        # Get User ID
        expert = User.query.filter_by(username=session["username"]).first()
        # Create our new  & Patient database entry
        pdf = Pdf(pdf_name=filename,
                  patient_id=form.patient_ID.data,
                  expert_id=expert.id,
                  lang=form.lang.data)
        patient = Patient(id=form.patient_ID.data,
                          patient_name=form.patient_nom.data,
                          patient_firstname=form.patient_prenom.data)
        # Check if the image or patient already exist in DB (same filename & patient ID)
        # If not: add it to DB
        if pdf.isduplicated() == False:
            pdf.set_pdfblob(os.path.join(temp_user_dir, filename))
            db.session.add(pdf)
            db.session.commit()

        if patient.existAlready() == False:
            db.session.add(patient)
            db.session.commit()

        # Finally delete the image file in temps folder and redirect to annotation
        if os.path.exists(os.path.join(temp_user_dir, filename)):
            os.remove(os.path.join(temp_user_dir, filename))
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
    """Render the annotation page after the upload of the initial image. 
    Redirects to the results page when the annotation form is submitted."""
    form = OcrForm()
    session["filename"] = request.args.get("filename")
    session["patient_ID"] = request.args.get("patient_ID")
    pdf_requested = Pdf.query.filter_by(
        pdf_name=session["filename"],
        patient_id=session["patient_ID"]).first()
    if pdf_requested != None and form.validate_on_submit(
    ) == False and pdf_requested.expert_id == current_user.id:
        session["pdf_expert_id"] = pdf_requested.expert_id
        # Create a temporary folder for username
        temp_user_dir = os.path.join(current_app.config["UPLOAD_FOLDER"],
                                     session["username"])
        if not os.path.exists(temp_user_dir):
            os.makedirs(temp_user_dir)
        # Write the PDF File
        filepath_to_write = os.path.join(temp_user_dir, pdf_requested.pdf_name)
        Ocr.write_file(pdf_requested.pdf_binary, filepath_to_write)
        session["filepath"] = os.path.join("temp", session["username"],
                                           pdf_requested.pdf_name)
        ocr_text_list = Ocr.pdf_to_text(session["filepath"],
                                        pdf_requested.lang)
        session["ocr_results_text"] = '\n##### NEW PAGE #####\n'.join(
            ocr_text_list)
        session["ocr_results_text"] = session["ocr_results_text"].split("\n")
    elif pdf_requested == None:
        flash('PDF doesn\'t exist!', "error")
        return redirect(url_for('ocr.upload_pdf'))
    elif pdf_requested.expert_id != current_user.id:
        flash('User not authorized for this PDF!', "error")
        return redirect(url_for('ocr.upload_pdf'))

    if form.validate_on_submit():
        # Save form data in the session cookie
        return redirect(url_for("ocr.write_ocr_report"))
    return render_template("ocr/ocr_results.html",
                           ocr_text=session["ocr_results_text"],
                           form=form,
                           filepath=session["filepath"])


@bp.route("/sucess_ocr", methods=["GET", "POST"])
def write_ocr_report():
    """Write the histological report and serve the results page for patient with download links"""
    # Write the histology report to file with first the basic informations
    temp_user_dir = os.path.join(current_app.config["UPLOAD_FOLDER"],
                                 session["username"])
    pdf_requested = Pdf.query.filter_by(
        pdf_name=session["filename"],
        patient_id=session["patient_ID"]).first()
    if pdf_requested != None:
        pdf_requested.report_text = str(session["ocr_results_text"])
        db.session.commit()
        shutil.rmtree(temp_user_dir)
    # Finally we render the results page
    return render_template("ocr/ocr_sucess.html")


@bp.route("/delete_pdf", methods=["GET", "POST"])
@login_required
def delete_pdf():
    pdf_requested = Pdf.query.filter_by(
        pdf_name=request.args.get("filename"),
        patient_id=request.args.get("patient_ID")).first()
    if pdf_requested != None and pdf_requested.expert_id == current_user.id:
        db.session.delete(pdf_requested)
        db.session.commit()
    return redirect(url_for('ocr.upload_pdf'))