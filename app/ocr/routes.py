import os
import json

from flask import flash, request, redirect, url_for
from flask import render_template, send_from_directory, current_app
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename

from app import db
from app.ocr import bp
from app.ocr.forms import PdfForm, OcrForm, DeleteButton
from app.models import Patient, Pdf
from app.ocr.ocr import Rapport


@bp.route("/data/<path:filename>")
@login_required
def data_folder(filename):
    """Serve files located in patient subfolder inside folder"""
    return send_from_directory(current_app.config["DATA_FOLDER"], filename)


@bp.route("/upload_pdf", methods=["GET", "POST"])
@login_required
def upload_pdf():
    """Page to upload a new PDF file."""
    form = PdfForm()
    delete_button = DeleteButton()
    pdf_history = Pdf.query.all()

    # if valid file uploaded: save it and create db entry
    if form.validate_on_submit():
        file = form.pdf.data
        filename = secure_filename(form.patient_ID.data + "_" + file.filename)

        # Create a data folder for patient
        data_patient_dir = os.path.join(
            current_app.config["DATA_FOLDER"], form.patient_ID.data
        )
        if not os.path.exists(data_patient_dir):
            os.makedirs(data_patient_dir)

        # Save the PDF to patient data folder
        file.save(os.path.join(data_patient_dir, filename))

        # Create our new PDF & Patient database entry
        pdf = Pdf(
            pdf_name=filename,
            patient_id=form.patient_ID.data,
            expert_id=current_user.id,
            lang=form.lang.data,
            pdf_path=os.path.join(data_patient_dir, filename),
        )
        patient = Patient(
            id=form.patient_ID.data,
            patient_name=form.patient_nom.data,
            patient_firstname=form.patient_prenom.data,
        )

        # Check if the PDF or patient already exist in DB (same filename & patient ID)
        # If not: add it to DB
        if not patient.exist_already():
            db.session.add(patient)

        if not pdf.isduplicated():
            db.session.add(pdf)

        db.session.commit()

        # Finally redirect to annotation
        return redirect(url_for("ocr.ocr_results", id=pdf.id))
    return render_template(
        "ocr_upload.html",
        form=form,
        pdf_history=pdf_history,
        delete_button=delete_button,
    )


@bp.route("/ocr_results", methods=["GET", "POST"])
@login_required
def ocr_results():
    """Perform OCR on PDF and render form to edit OCR results."""
    form = OcrForm()
    # Query the database from arg in get request
    pdf_requested = Pdf.query.get(request.args.get("id"))

    # If PDF exist in database: serve it
    if pdf_requested is not None and not form.validate_on_submit():
        pdf_object = Rapport(path=pdf_requested.pdf_path, lang=pdf_requested.lang)
        rel_filepath = os.path.join(
            "data", pdf_requested.patient_id, pdf_requested.pdf_name
        )

        # Perform OCR on the PDF file if no text registered in DB
        if pdf_requested.ocr_text is None:
            pdf_object.pdf_to_text()
            ocr_text = pdf_object.raw_text
        else:
            ocr_text = pdf_requested.ocr_text

        form.ocr_text.data = ocr_text

    # If OCR is finished and submitted: update database entry
    elif pdf_requested is not None and form.validate_on_submit():
        pdf_requested.ocr_text = form.ocr_text.data
        db.session.commit()
        return redirect(url_for("ocr.upload_pdf"))

    # Error handling
    elif pdf_requested is None:
        flash("PDF doesn't exist!", "error")
        return redirect(url_for("ocr.upload_pdf"))

    # Base Page
    return render_template(
        "ocr_results.html",
        form=form,
        ocr_text=ocr_text,
        patient_id=request.args.get("patient_id"),
        rel_filepath=rel_filepath,
    )


@bp.route("/delete_pdf/<id_pdf>", methods=["POST"])
@login_required
def delete_pdf(id_pdf):
    """Page delete a histology report from database with delete button."""
    form = DeleteButton()
    # Retrieve database entry and delete it if existing
    if form.validate_on_submit():
        pdf = Pdf.query.get(id_pdf)
        if pdf is None:
            flash("PDF {} not found.".format(id_pdf), "danger")
            return redirect(url_for("ocr.upload_pdf"))
        db.session.delete(pdf)
        db.session.commit()
        flash("Deleted PDF entry {}!".format(id_pdf), "success")
        return redirect(url_for("ocr.upload_pdf"))
    else:
        return redirect(url_for("ocr.upload_pdf"))
