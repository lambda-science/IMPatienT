import os
from contextlib import suppress
import json
from app import db
from app.imgupload import bp
from app.imgupload.forms import DeleteButton, ImageForm
from app.models import Image
from flask import (
    current_app,
    flash,
    redirect,
    render_template,
    request,
    send_from_directory,
    url_for,
    make_response,
)
from flask_login import current_user, login_required
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename
from PIL import Image as PILImage
import pandas as pd
import tarfile


@bp.route("/data/images/<path:filename>")
@login_required
def images_folder(filename):
    """Route to serve files located in the data/images folder.

    Args:
        filename (str): Path to the filename inside the data/images folder.

    Returns:
        File: returns the file
    """
    return send_from_directory(current_app.config["IMAGES_FOLDER"], filename)


@bp.route("/img_index", methods=["GET", "POST"])
@login_required
def img_index():
    """View function for the image index

    Returns:
        str: Image Index HTML Page
    """
    form = DeleteButton()
    image_history = Image.query.all()
    return render_template("img_index.html", form=form, image_history=image_history)


@bp.route("/img_index/download", methods=["GET"])
@login_required
def img_download():
    df = pd.read_sql(db.session.query(Image).statement, db.session.bind)
    df.to_csv(os.path.join(current_app.config["IMAGES_FOLDER"], "images_db.csv"))
    with tarfile.open(
        os.path.join(current_app.config["DATA_FOLDER"], "image_data.tar.gz"), "w:gz"
    ) as tar:
        tar.add(
            current_app.config["IMAGES_FOLDER"],
            arcname=os.path.basename(current_app.config["IMAGES_FOLDER"]),
        )
    return send_from_directory(current_app.config["DATA_FOLDER"], "image_data.tar.gz")


@bp.route("/delete_img/<id_img>", methods=["POST"])
@login_required
def delete_img(id_img):
    """Route for the deletion of an image from the database and data folder.

    Args:
        id_img (int): ID of the image to delete

    Returns:
        redirect: Redirect to the image index HTML page
    """
    form = DeleteButton()
    # Retrieve database entry and delete it if existing
    if form.validate_on_submit():
        image = Image.query.get(id_img)
        if image is None:
            flash("Image {} not found.".format(id_img), "danger")
            return redirect(url_for("imgupload.img_index"))
        try:  # nosec
            os.remove(
                os.path.join(current_app.config["IMAGES_FOLDER"], image.image_path)
            )
            os.remove(
                os.path.join(current_app.config["IMAGES_FOLDER"], image.mask_annot_path)
            )
            os.remove(
                os.path.join(current_app.config["IMAGES_FOLDER"], image.seg_matrix_path)
            )
            os.remove(
                os.path.join(current_app.config["IMAGES_FOLDER"], image.classifier_path)
            )
            os.remove(
                os.path.join(
                    current_app.config["IMAGES_FOLDER"], image.blend_image_path
                )
            )
            os.remove(
                os.path.join(current_app.config["IMAGES_FOLDER"], image.mask_image_path)
            )
        except:  # nosec
            pass  # nosec
        db.session.delete(image)
        db.session.commit()
        flash("Deleted Image entry {}!".format(id_img), "success")
        return redirect(url_for("imgupload.img_index"))
    else:
        return redirect(url_for("imgupload.img_index"))


@bp.route("/create_img", methods=["GET", "POST"])
@login_required
def create_img():
    """View function for the image upload page.

    Returns:
        str: Image upload HTML page and form and redirects to the image index.
    """
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

        # If Image is a Tiff, save a PNG format
        print(filename.split("."))
        if filename.split(".")[-1] in ["tiff", "tif", "TIFF", "TIF"]:
            image = PILImage.open(file)
            filename_back = ".".join(filename.split(".")[0:-1]) + ".png"
            image.save(os.path.join(data_patient_dir, filename_back), "PNG")
        else:
            filename_back = filename
        # Create our new Image & Patient database entry
        print(os.path.join(data_patient_dir, filename_back))
        image = Image(
            image_name=filename,
            expert_id=current_user.id,
            patient_id=form.patient_ID.data,
            biopsy_id=form.biopsy_report_ID.data,
            type_coloration=form.type_coloration.data,
            age_at_biopsy=form.age_histo.data,
            image_path=os.path.join(data_patient_dir, filename),
            image_background_path=os.path.join(data_patient_dir, filename_back),
        )

        with suppress(json.decoder.JSONDecodeError):
            image.diagnostic = json.loads(form.diagnostic.data)[0]["value"]
        # Check if the image already exist in DB (same filename & patient ID)
        # If not: add it to DB

        if not image.isduplicated():
            db.session.add(image)

        db.session.commit()

        # Finally redirect to annotation
        return redirect(url_for("imgupload.img_index"))
    return render_template("create_img.html", form=form)
