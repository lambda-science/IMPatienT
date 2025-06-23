import os

import impatient.app.src.common as Common
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField, FileRequired
from wtforms import SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, Regexp


class ImageForm(FlaskForm):
    """Form for uploading images.

    Args:
        FlaskForm (FlaskForm Class): The FlaskForm Class
    """

    image = FileField(
        validators=[
            FileRequired(),
            FileAllowed(
                ["png", "jpg", "jpeg", "tif", "tiff", "TIF", "TIFF"],
                "This file is not a valid image !",
            ),
        ],
        render_kw={"class": "form-control-file border"},
    )
    patient_ID = StringField(
        "Patient ID",
        validators=[DataRequired(), Regexp(r"^[\w.-_]+$")],
        render_kw={"placeholder": "Patient ID", "class": "form-control"},
    )
    biopsy_report_ID = StringField(
        "Biopsy ID",
        render_kw={"placeholder": "Biopsy Report ID", "class": "form-control"},
    )
    type_coloration = SelectField(
        "Coloration Type",
        validators=[DataRequired()],
        choices=[
            "Haematoxylin and Eosin stain (HE)",
            "Gömöri trichrome stain (TG)",
            "Adenosine Triphosphate Staining (ATP)",
            "NADH/SDH staining",
            "COX staining",
            "PAS staining",
            "Sudan Lipids staining",
            "Phosphorylases staining",
            "Electron Microscopy (EM)",
        ],
        render_kw={
            "placeholder": "Histology Coloration Type",
            "class": "form-control custom-select",
        },
    )
    age_histo = SelectField(
        "Age of patient at biopsy",
        validators=[DataRequired()],
        choices=[i for i in range(131)],
        render_kw={
            "placeholder": "Patient age at histology sample time",
            "class": "form-control custom-select",
        },
    )
    diagnostic = StringField(
        "Diagnosis (Orphanet API)",
        render_kw={
            "placeholder": "Disease diagnostic",
            "class": "form-control",
        },
    )

    # submit = SubmitField("Upload", render_kw={"class": "btn btn-primary mb-2"})


class DeleteButton(FlaskForm):
    """Empty form for the delete button.

    Args:
        FlaskForm (FlaskForm Class): The FlaskForm Class
    """

    submit = SubmitField("Confirm Deletion", render_kw={"class": "btn btn-danger"})
