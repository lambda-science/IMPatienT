import os

from flask import flash, request, redirect, url_for, render_template
from flask import send_from_directory, current_app
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage

from app import db
from app.imgupload import bp
from app.imgupload.forms import ImageForm, DeleteButton
from app.models import Image


@bp.route("/data/images/<path:filename>")
@login_required
def images_folder(filename):
    """Serve files located in patient subfolder inside folder"""
    return send_from_directory(current_app.config["IMAGES_FOLDER"], filename)


@bp.route("/img_index", methods=["GET", "POST"])
@login_required
def img_index():
    """Image Index Page"""
    form = DeleteButton()
    image_history = Image.query.all()

    return render_template("img_index.html", form=form, image_history=image_history)


@bp.route("/delete_img/<id_img>", methods=["POST"])
@login_required
def delete_img(id_img):
    """Page delete a histology report from database with delete button."""
    form = DeleteButton()
    # Retrieve database entry and delete it if existing
    if form.validate_on_submit():
        image = Image.query.get(id_img)
        if image is None:
            flash("Image {} not found.".format(id_img), "danger")
            return redirect(url_for("imgupload.img_index"))
        try:
            os.remove(os.path.join(current_app.config["IMAGES_FOLDER"],image.image_path))
            os.remove(os.path.join(current_app.config["IMAGES_FOLDER"],image.mask_annot_path))
            os.remove(os.path.join(current_app.config["IMAGES_FOLDER"],image.seg_matrix_path))
            os.remove(os.path.join(current_app.config["IMAGES_FOLDER"],image.classifier_path))
            os.remove(os.path.join(current_app.config["IMAGES_FOLDER"],image.bland_image_path))
            os.remove(os.path.join(current_app.config["IMAGES_FOLDER"],image.mask_image_path))            
        except:
            pass
        db.session.delete(image)
        db.session.commit()
        flash("Deleted Image entry {}!".format(id_img), "success")
        return redirect(url_for("imgupload.img_index"))
    else:
        return redirect(url_for("imgupload.img_index"))


@bp.route("/create_img", methods=["GET", "POST"])
@login_required
def create_img():
    # If args in URL, try to retrive report from DB and pre-fill it
    if request.args:
        image_request = Image.query.get(request.args.get("id"))
        if image_request is not None:
            file = None
            with open(image_request.image_path, "rb") as fp:
                file = FileStorage(fp)
            form = ImageForm(
                image=file,
                patient_ID=image_request.patient_id,
                biopsy_report_ID=image_request.biopsy_id,
                type_coloration=image_request.type_coloration,
                age_histo=image_request.age_at_biopsy,
                diagnostic=image_request.diagnostic,
            )

        else:
            return redirect(url_for("imgupload.img_index"))
    # If no args: empty form
    else:
        form = ImageForm()

    if form.validate_on_submit():
        file = form.image.data
        patient_id = form.patient_ID.data
        filename = secure_filename(patient_id + "_" + file.filename)

        # Create a data folder for patient
        data_patient_dir = os.path.join(current_app.config["IMAGES_FOLDER"], patient_id)
        if not os.path.exists(data_patient_dir):
            os.makedirs(data_patient_dir)
        # Save the image to patient data folder
        file.save(os.path.join(data_patient_dir, filename))
        # Create our new Image & Patient database entry
        image = Image(
            image_name=filename,
            expert_id=current_user.id,
            patient_id=form.patient_ID.data,
            biopsy_id=form.biopsy_report_ID.data,
            type_coloration=form.type_coloration.data,
            age_at_biopsy=form.age_histo.data,
            image_path=os.path.join(data_patient_dir, filename),
            diagnostic=form.diagnostic.data,
        )
        # Check if the image already exist in DB (same filename & patient ID)
        # If not: add it to DB

        if not image.isduplicated():
            db.session.add(image)

        db.session.commit()

        # Finally redirect to annotation
        return redirect(url_for("imgupload.img_index"))
    return render_template("create_img.html", form=form)
